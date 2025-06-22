import requests
import logging
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from .models import Project, IntelligenceEngineering # Pastikan IntelligenceEngineering diimpor

logger = logging.getLogger(__name__)

# --- FUNGSI BANTUAN UNTUK MENDAPATKAN HEADERS ---
def _get_api_headers():
    headers = {}
    if hasattr(settings, 'EXTERNAL_API_AUTH_TOKEN') and settings.EXTERNAL_API_AUTH_TOKEN:
        headers['Authorization'] = f'Token {settings.EXTERNAL_API_AUTH_TOKEN}'
    return headers

# --- FUNGSI SINKRONISASI UNTUK PROYEK (DARI API KELOMPOK LAIN) ---
# Tidak ada perubahan pada fungsi ini karena fokusnya adalah pada IE Sync
def sync_projects_from_external_api(request=None):
    api_url = settings.EXTERNAL_PROJECT_MENEJ_API_URL
    headers = _get_api_headers()

    logger.info(f"[Project Sync] Attempting to sync projects from API: {api_url}")

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        external_projects_data = response.json()

        if not isinstance(external_projects_data, list):
            logger.warning("[Project Sync] External Project API did not return a list. Assuming single object and wrapping in a list.")
            external_projects_data = [external_projects_data]

        logger.info(f"[Project Sync] Successfully parsed JSON. Number of projects received: {len(external_projects_data)}")

        projects_synced_count = 0

        for project_data in external_projects_data:
            external_id = project_data.get('id')
            name = project_data.get('nama_proyek')
            description = project_data.get('deskripsi_proyek')
            location = project_data.get('lokasi', 'N/A')
            start_date_str = project_data.get('tanggal_mulai')
            end_date_str = project_data.get('tanggal_selesai')

            # Get raw status from API, default to 'Planning' if not provided
            raw_status_from_api = project_data.get('status', 'Planning')

            # Get supervisor name directly from API
            supervisor_name = project_data.get('supervisor_proyek', '')

            if not all([external_id, name]):
                logger.warning(f"[Project Sync] Skipping project: Missing essential data (id or nama_proyek). Data: {project_data}")
                continue

            start_date = None
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"[Project Sync] Invalid start_date format for project {name} (ID: {external_id}): {start_date_str}. Expected YYYY-MM-DD. Skipping date.")

            end_date = None
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"[Project Sync] Invalid end_date format for project {name} (ID: {external_id}): {end_date_str}. Expected YYYY-MM-DD. Skipping date.")

            status_api_to_model_map = {
                'berlangsung': 'Ongoing',
                'stop': 'Stop',
                'done': 'Done',
                'planning': 'Planning',
                'pending': 'Pending',
            }

            mapped_status = status_api_to_model_map.get(raw_status_from_api.lower(), 'Pending')

            if mapped_status == 'Pending' and raw_status_from_api.lower() not in status_api_to_model_map:
                logger.warning(f"[Project Sync] Status '{raw_status_from_api}' from API not found in Project.STATUS_CHOICES or map. Defaulting to 'Pending'.")

            try:
                project, created = Project.objects.update_or_create(
                    external_id=external_id,
                    defaults={
                        'name': name,
                        'description': description,
                        'location': location,
                        'start_date': start_date,
                        'end_date': end_date,
                        'status': mapped_status,
                        'supervisor': supervisor_name,
                    }
                )
                if created:
                    logger.info(f"[Project Sync] New project '{name}' (ID: {external_id}) created from external API.")
                else:
                    logger.info(f"[Project Sync] Project '{name}' (ID: {external_id}) updated from external API.")

                projects_synced_count += 1

            except Exception as db_e:
                logger.error(f"[Project Sync] ERROR SAVING PROJECT '{name}' (ID: {external_id}) to DB: {db_e}. Data: {project_data}", exc_info=True)
                if request: messages.error(request, f"Gagal menyimpan proyek '{name}' (ID: {external_id}): {db_e}")

        if projects_synced_count > 0:
            if request: messages.success(request, f"Proyek berhasil disinkronkan dari API eksternal. ({projects_synced_count} proyek diproses).")
            return True
        else:
            if request: messages.warning(request, "Sinkronisasi proyek selesai, tetapi tidak ada proyek yang berhasil disimpan atau diperbarui.")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"[Project Sync] Error fetching projects from external API: {e}", exc_info=True)
        if request: messages.error(request, f"Gagal menyinkronkan proyek: {e}")
        return False
    except ValueError as e:
        logger.error(f"[Project Sync] Error decoding JSON response from Project API: {e}. Response was: {response.text if 'response' in locals() else 'No response object'}", exc_info=True)
        if request: messages.error(request, f"Gagal memproses data Project API: {e}. Pastikan respons adalah JSON yang valid.")
        return False
    except Exception as e:
        logger.error(f"[Project Sync] An unexpected error occurred during project synchronization: {e}", exc_info=True)
        if request: messages.error(request, f"Terjadi kesalahan tak terduga saat sinkronisasi proyek: {e}")
        return False


# --- FUNGSI SINKRONISASI UNTUK INTELLIGENCE ENGINEERING (Disesuaikan) ---
def sync_intelligence_engineering_from_external_api(request=None):
    api_url = settings.EXTERNAL_PROJECT_ENGINEER_API_URL
    headers = _get_api_headers()

    logger.info(f"[IE Sync] Attempting to sync Intelligence Engineering from API: {api_url}")

    synced_count = 0
    skipped_count = 0
    total_entries_received = 0

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        external_ie_data = response.json()

        if not isinstance(external_ie_data, list):
            logger.warning("[IE Sync] External IE API did not return a list. Wrapped single object in a list.")
            external_ie_data = [external_ie_data]

        total_entries_received = len(external_ie_data)
        logger.info(f"[IE Sync] Successfully parsed JSON. Number of IE entries received: {total_entries_received}")

        for ie_data in external_ie_data:
            external_id_from_api = ie_data.get('id') # Ini adalah external_id proyek

            if not external_id_from_api:
                logger.warning("[IE Sync] Skipping IE sync: 'id' (project external ID) missing in API response for an IE entry. Data: %s", ie_data)
                skipped_count += 1
                if request:
                    messages.warning(request, f"Melewatkan sinkronisasi IE: 'id' proyek hilang dari salah satu entri API. Data: {ie_data}")
                continue

            try:
                # Cari proyek lokal berdasarkan external_id yang sama dengan 'id' dari IE API
                related_project = Project.objects.get(external_id=external_id_from_api)
                logger.info(f"[IE Sync] Found related project for IE: {related_project.name} (External ID: {external_id_from_api})")
            except Project.DoesNotExist:
                logger.warning(f"[IE Sync] Skipping IE sync for IE with project external ID '{external_id_from_api}': Related Project not found in local DB. Sync Projects first!")
                skipped_count += 1
                if request:
                    messages.error(request, f"Gagal menyinkronkan IE untuk proyek ID eksternal '{external_id_from_api}': Proyek tidak ditemukan secara lokal. Sinkronkan proyek terlebih dahulu.")
                continue
            except Exception as e:
                logger.error(f"[IE Sync] Error finding related project for IE ID '{external_id_from_api}': {e}", exc_info=True)
                skipped_count += 1
                if request:
                    messages.error(request, f"Kesalahan saat mencari proyek terkait untuk ID IE eksternal '{external_id_from_api}': {e}. Entri ini dilewati.")
                continue

            # --- AMBIL DAN PROSES HANYA FIELD YANG DISEDIAKAN OLEH API ---
            # Pastikan Anda telah memperbarui model IntelligenceEngineering Anda
            # untuk hanya mencakup field-field yang relevan dengan API ini.
            # Jika model Anda masih memiliki field lama, mereka akan diisi dengan None/default.

            meaningful_objectives_data = ie_data.get('meaningful_objectives') or {}

            # Mendapatkan data individu dari meaningful_objectives_data
            mo_organizational = meaningful_objectives_data.get('organizational')
            mo_leading_indicators = meaningful_objectives_data.get('leading_indicators')
            mo_user_outcomes = meaningful_objectives_data.get('user_outcomes')
            mo_model_properties = meaningful_objectives_data.get('model_properties')

            # --- Update/Create IntelligenceEngineering instance ---
            # Kita menggunakan project sebagai kunci unik untuk update_or_create karena ini OneToOneField
            ie_instance, created = IntelligenceEngineering.objects.update_or_create(
                project=related_project,
                defaults={
                    'external_id_ie': external_id_from_api, # Menyimpan external_id_ie (id proyek dari API IE)
                    'mo_organizational': mo_organizational,
                    'mo_leading_indicators': mo_leading_indicators,
                    'mo_user_outcomes': mo_user_outcomes,
                    'mo_model_properties': mo_model_properties,
                }
            )
            if created:
                logger.info(f"[IE Sync] New Intelligence Engineering for project '{related_project.name}' (IE external ID: {external_id_from_api}) created from external API.")
            else:
                logger.info(f"[IE Sync] Intelligence Engineering for project '{related_project.name}' (IE external ID: {external_id_from_api}) updated from external API.")
            synced_count += 1

        # --- Final messages and return value ---
        if request:
            if synced_count > 0:
                messages.success(request, f"Data Rekayasa Kecerdasan berhasil disinkronkan. ({synced_count} diperbarui/dibuat)")
            if skipped_count > 0:
                messages.info(request, f"Beberapa entri Rekayasa Kecerdasan dilewati karena masalah proyek terkait atau data hilang. ({skipped_count} dilewati)")
            if synced_count == 0 and skipped_count == total_entries_received and total_entries_received > 0:
                messages.warning(request, "Tidak ada entri Rekayasa Kecerdasan yang berhasil disinkronkan. Semua entri dilewati.")
            elif total_entries_received == 0:
                messages.info(request, "Tidak ada data Rekayasa Kecerdasan yang diterima dari API eksternal.")

        # Return True if the overall API call was successful, regardless of skipped entries
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"[IE Sync] Error fetching Intelligence Engineering from external API: {e}", exc_info=True)
        if request: messages.error(request, f"Gagal menyinkronkan Rekayasa Kecerdasan: Kesalahan koneksi atau respons API tidak valid. Detail: {e}")
        return False
    except ValueError as e:
        logger.error(f"[IE Sync] Error decoding JSON response for IE API: {e}. Response was: {response.text if 'response' in locals() else 'No response object'}", exc_info=True)
        if request: messages.error(request, f"Gagal memproses data Rekayasa Kecerdasan dari API (JSON invalid). Detail: {e}")
        return False
    except Exception as e:
        logger.error(f"[IE Sync] An unexpected error occurred during IE synchronization: {e}", exc_info=True)
        if request: messages.error(request, f"Terjadi kesalahan tak terduga saat sinkronisasi Rekayasa Kecerdasan: {e}")
        return False
