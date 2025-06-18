import requests
import logging
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from .models import Project, IntelligenceEngineering
# from django.contrib.auth import get_user_model # No longer needed if not linking to User model

logger = logging.getLogger(__name__)
# User = get_user_model() # No longer needed if not linking to User model

# --- FUNGSI BANTUAN UNTUK MENDAPATKAN HEADERS ---
def _get_api_headers():
    headers = {}
    if hasattr(settings, 'EXTERNAL_API_AUTH_TOKEN') and settings.EXTERNAL_API_AUTH_TOKEN:
        headers['Authorization'] = f'Token {settings.EXTERNAL_API_AUTH_TOKEN}' 
    return headers

# --- FUNGSI SINKRONISASI UNTUK PROYEK (DARI API KELOMPOK LAIN) ---
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
            supervisor_name = project_data.get('supervisor_proyek', '') # Default to empty string if not provided

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

            # --- UPDATED STATUS MAPPING LOGIC ---
            # Define a mapping from API status (lowercase) to your Project.STATUS_CHOICES values
            status_api_to_model_map = {
                'berlangsung': 'Ongoing',
                'stop': 'Stop',
                'done': 'Done',
                'planning': 'Planning',
                'pending': 'Pending',
                # Add any other specific mappings if your API uses different terms
            }
            
            # Attempt to map the status from API. If not found, use a fallback (e.g., 'Pending').
            # The .lower() is important for case-insensitive matching.
            mapped_status = status_api_to_model_map.get(raw_status_from_api.lower(), 'Pending')

            # Log a warning if the status wasn't directly mapped and is not 'Pending' (meaning it was an unrecognised status)
            if mapped_status == 'Pending' and raw_status_from_api.lower() not in status_api_to_model_map:
                logger.warning(f"[Project Sync] Status '{raw_status_from_api}' from API not found in Project.STATUS_CHOICES or map. Defaulting to 'Pending'.")
            # --- END UPDATED STATUS MAPPING LOGIC ---

            # --- REMOVED SUPERVISOR USER LOOKUP ---
            # The supervisor_obj lookup is no longer needed as 'supervisor' is now a CharField
            # We will directly use 'supervisor_name' from the API
            # --- END REMOVED SUPERVISOR USER LOOKUP ---

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
                        'supervisor': supervisor_name, # Directly assign the string name here
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


# --- FUNGSI SINKRONISASI UNTUK INTELLIGENCE ENGINEERING ---
# No changes needed here based on the current problem.
def sync_intelligence_engineering_from_external_api(request=None): 
    api_url = settings.EXTERNAL_PROJECT_ENGINEER_API_URL 
    headers = _get_api_headers() 
    
    logger.info(f"[IE Sync] Attempting to sync Intelligence Engineering from API: {api_url}") 

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status() 
        external_ie_data = response.json()

        if not isinstance(external_ie_data, list):
            logger.warning("[IE Sync] External IE API did not return a list. Wrapped single object in a list.") 
            external_ie_data = [external_ie_data]

        logger.info(f"[IE Sync] Successfully parsed JSON. Number of IE entries received: {len(external_ie_data)}") 

        for ie_data in external_ie_data:
            external_id_from_api = ie_data.get('id_proyek') 
            
            if not external_id_from_api:
                logger.warning("[IE Sync] Skipping IE sync: 'id_proyek' missing in API response for an IE entry. Data: %s", ie_data) 
                continue

            try:
                related_project = Project.objects.get(external_id=external_id_from_api)
                logger.info(f"[IE Sync] Found related project for IE: {related_project.name} (External ID: {external_id_from_api})")
            except Project.DoesNotExist:
                logger.warning(f"[IE Sync] Skipping IE sync for IE with 'id_proyek' {external_id_from_api}: Related Project not found in local DB. Sync Projects first!") 
                if request:
                    messages.error(request, f"Gagal menyinkronkan IE untuk proyek ID {external_id_from_api}: Proyek tidak ditemukan secara lokal. Sinkronkan proyek terlebih dahulu.")
                continue 
            except Exception as e:
                logger.error(f"[IE Sync] Error finding related project for IE ID {external_id_from_api}: {e}", exc_info=True) 
                continue


            meaningful_objectives = ie_data.get('meaningful_objectives', {})
            intelligence_experience = ie_data.get('intelligence_experience', {})
            intelligence_implementation = ie_data.get('intelligence_implementation', {})
            batasan_pengembangan = ie_data.get('batasan_pengembangan', {})
            status_realisasi = ie_data.get('status_realisasi', {})
            perencanaan = ie_data.get('perencanaan', {})

            ie_instance, created = IntelligenceEngineering.objects.update_or_create(
                project=related_project,
                defaults={
                    'mo_organizational': meaningful_objectives.get('organizational'),
                    'mo_leading_indicators': meaningful_objectives.get('leading_indicators'),
                    'mo_user_outcomes': meaningful_objectives.get('user_outcomes'),
                    'mo_model_properties': meaningful_objectives.get('model_properties'),

                    'ie_automate': intelligence_experience.get('automate'),
                    'ie_prompt': intelligence_experience.get('prompt'),
                    'ie_annotate': intelligence_experience.get('annotate'),
                    'ie_organization': intelligence_experience.get('organization'),
                    'ie_system_objectives': intelligence_experience.get('system_objectives'),
                    'ie_minimize_flaws': intelligence_experience.get('minimize_flaws'),
                    'ie_create_data': intelligence_experience.get('create_data'),

                    'ii_business_process': intelligence_implementation.get('business_process'),
                    'ii_technology': intelligence_implementation.get('technology'),
                    'ii_build_process': intelligence_implementation.get('build_process'),

                    'bd_limitation': batasan_pengembangan.get('limitation'),
                    'sr_realization': status_realisasi.get('realization'),
                    'pr_deployment': perencanaan.get('deployment'),
                    'pr_maintenance': perencanaan.get('maintenance'),
                    'pr_operating': perencanaan.get('operating'),
                }
            )
            if created:
                logger.info(f"[IE Sync] New Intelligence Engineering for project '{related_project.name}' created from external API.") 
            else:
                logger.info(f"[IE Sync] Intelligence Engineering for project '{related_project.name}' updated from external API.") 
        
        if request: messages.success(request, "Data Rekayasa Kecerdasan berhasil disinkronkan dari API eksternal.")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"[IE Sync] Error fetching Intelligence Engineering from external API: {e}", exc_info=True) 
        if request: messages.error(request, f"Gagal menyinkronkan Rekayasa Kecerdasan: {e}")
        return False
    except ValueError as e: 
        logger.error(f"[IE Sync] Error decoding JSON response for IE API: {e}. Response was: {response.text if 'response' in locals() else 'No response object'}", exc_info=True) 
        if request: messages.error(request, f"Gagal memproses data Rekayasa Kecerdasan dari API: {e}")
        return False
    except Exception as e:
        logger.error(f"[IE Sync] An unexpected error occurred during IE synchronization: {e}", exc_info=True) 
        if request: messages.error(request, f"Terjadi kesalahan tak terduga saat sinkronisasi Rekayasa Kecerdasan: {e}")
        return False