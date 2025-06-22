from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, logout, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfileForm, ProjectForm, ProblemFramingForm, DatasetRequestForm, UserUpdateForm, IntelligenceEngineeringForm, DataProcessingForm, TrainingModelForm, IntelligenceEngineering
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import requests # Import library requests
import logging # Untuk logging error
from datetime import datetime # Import datetime untuk penanganan tanggal
from django.db.models import Count # Import Count untuk agregasi


from .utils import sync_projects_from_external_api, \
                   sync_intelligence_engineering_from_external_api
logger = logging.getLogger(__name__)

from .models import Project, ProblemFraming, DatasetRequest, Profile, TrainingModel, DataProcessing, DatasetReply, Document

# Create your views here.
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('projek:dashboard')
    else:
        return render(request, 'landing_pages/landing_page.html')

#login
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('projek:dashboard')  # redirect ke halaman setelah login
            else:
                messages.error(request, 'Username atau password salah.')
        else:
            messages.error(request, 'Username atau password tidak valid.')
    else:
        form = AuthenticationForm()

    return render(request, 'login_pages/login.html', {'form': form})

# register
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            form.save()
            auth_login(request, user)
            messages.success(request, 'Pendaftaran berhasil! Anda sekarang masuk.')
            return redirect('projek:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'login_pages/register.html', {'form': form})

#logout
def logout_view(request):
    logout(request)
    return redirect('projek:login')

#profile
@login_required
def profile_view(request):
    # Mengakses objek Profile terkait dari request.user
    user_profile = request.user.profile
    context = {
        'page_title': f'Profil Pengguna: {request.user.username}',
        'user_obj': request.user, # Mengirim objek User
        'profile_obj': user_profile, # Mengirim objek Profile Anda
    }
    return render(request, 'profile/profile.html', context)

@login_required
def profile_update_view(request):
    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileForm(instance=request.user.profile)

    if request.method == 'POST':
        if 'submit_account' in request.POST: # Cek apakah tombol "Perbarui Akun" ditekan
            u_form = UserUpdateForm(request.POST, instance=request.user)
            if u_form.is_valid():
                u_form.save()
                messages.success(request, 'Informasi akun Anda berhasil diperbarui!')
                return redirect('projek:profile_update') # Redirect ke halaman edit profil
            else:
                messages.error(request, 'Terjadi kesalahan saat memperbarui informasi akun. Mohon periksa input Anda.')

        elif 'submit_profile' in request.POST: # Cek apakah tombol "Perbarui Profil" ditekan
            p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
            if p_form.is_valid():
                p_form.save()
                messages.success(request, 'Detail profil Anda berhasil diperbarui!')
                return redirect('projek:profile_update') # Redirect ke halaman edit profil
            else:
                messages.error(request, 'Terjadi kesalahan saat memperbarui detail profil. Mohon periksa input Anda.')

    context = {
        'page_title': f'Edit Profil: {request.user.username}',
        'u_form': u_form,
        'p_form': p_form,
        'user_obj': request.user,
    }
    return render(request, 'profile/edit_profile.html', context)



#dashboard
@login_required
def dashboard(request):
    if request.method == 'POST':
        if 'sync_projects' in request.POST:
            sync_projects_from_external_api(request)
        elif 'sync_intelligence_engineering' in request.POST:
            sync_intelligence_engineering_from_external_api(request)

        return redirect('projek:dashboard') # Redirect kembali ke dashboard setelah sinkronisasi

    projects = Project.objects.all().order_by('-created_at')
    intelligence_engineerings = IntelligenceEngineering.objects.filter(project__in=projects).order_by('-created_at')

    # --- Data untuk Statistik Dashboard ---

    # 1. Statistik Proyek (berdasarkan Status)
    project_status_counts_raw = Project.objects.values('status').annotate(count=Count('status'))
    project_status_labels = []
    project_status_data = []

    # Mapping status value to its display name for chart labels
    status_display_map = dict(Project.STATUS_CHOICES)

    for item in project_status_counts_raw:
        display_name = status_display_map.get(item['status'], item['status']) # Get display name, fallback to raw if not found
        project_status_labels.append(display_name)
        project_status_data.append(item['count'])

    # 2. Total Entri Rekayasa Kecerdasan
    total_ie_entries = IntelligenceEngineering.objects.count()

    # 3. Total Balasan Dataset
    total_dataset_replies = DatasetReply.objects.count()

    # 4. Total Model Pelatihan
    total_training_models = TrainingModel.objects.count()

    chart_data = {
        'projectStatusLabels': project_status_labels,
        'projectStatusData': project_status_data,
        'totalIeEntries': total_ie_entries,
        'totalDatasetReplies': total_dataset_replies,
        'totalTrainingModels': total_training_models,
    }

    context = {
        'page_title': 'Dashboard Utama',
        'projects': projects,
        'intelligence_engineerings': intelligence_engineerings,
        'chart_data': chart_data, # Tambahkan data statistik ke konteks
    }
    return render(request, 'dashboard/dashboard.html', context)

#projek
@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            # Jika supervisor tidak diisi di form, set ke user yang sedang login
            if not project.supervisor:
                project.supervisor = request.user
            project.save()
            messages.success(request, f"Proyek '{project.name}' berhasil dibuat!")
            return redirect('projek:list_projek')
        else:
            messages.error(request, "Terjadi kesalahan saat membuat proyek. Silakan periksa isian Anda.")
    else:
        form = ProjectForm()

    context = {
        'form': form,
        'page_title': 'Buat Proyek Baru'
    }
    return render(request, 'projek/create_project.html', context)

@login_required
def project_list_view(request):
    projects = Project.objects.all().order_by('-created_at')
    context = {
        'projects': projects,
        'page_title': 'Daftar Proyek Manajemen'
        }
    return render(request, 'projek/projek_list.html', context)

@login_required
def project_detail_view(request, project_id):
    """
    View untuk menampilkan detail satu proyek.
    """
    project = get_object_or_404(Project, id=project_id)
    context = {
        'project': project,
        'page_title': f"Detail Proyek: {project.name}"
    }
    return render(request, 'projek/project_detail.html', context)

@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"Proyek '{project.name}' berhasil diperbarui!")
            return redirect('projek:list_projek')
        else:
            messages.error(request, "Terjadi kesalahan saat memperbarui proyek.")
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
        'page_title': f"Edit Proyek: {project.name}"
    }
    return render(request, 'projek/create_project.html', context)

@login_required
def delete_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        project.delete()
        messages.success(request, f" '{project.name}' berhasil dihapus.")
        return redirect('projek:dashboard')
    else:
        # Untuk permintaan GET, render halaman konfirmasi
        context = {
            'project': project,
            'page_title': f"Hapus: {project.name}"
        }
        return render(request, 'projek/confirm_delete_project.html', context)


#integrasi intelligence engiinering :
@login_required
def intelligence_engineering_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    try:
        ie_instance = IntelligenceEngineering.objects.get(project=project)
    except IntelligenceEngineering.DoesNotExist:
        ie_instance = None

    context = {
        'project': project,
        'ie_instance': ie_instance,
        'page_title': f"Detail Rekayasa Kecerdasan: {project.name}"
    }
    return render(request, 'intelligence_engineering/intelligence_engineering_detail.html', context)


## Problem Framing (CRUD Problem Framing)
@login_required
def select_problem_framings(request):
    projects_for_framing = Project.objects.filter(problem_framing__isnull=True).order_by('name')
    context = {
        'projects': projects_for_framing,
        'page_title': 'Pilih Proyek untuk Problem Framing'
    }
    return render(request, 'problem_framing/select_problem_framing.html', context)

@login_required
def create_problem_framing_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if hasattr(project, 'problem_framing') and project.problem_framing:
        messages.warning(request, f"Proyek '{project.name}' sudah memiliki entri Problem Framing. Silakan edit jika perlu.")
        return redirect('projek:edit_problem_framing', pk=project.problem_framing.pk)

    intelligence_engineering_form = None # Ini akan menyimpan instance formulir read-only

    try:
        intelligence_engineering_instance = IntelligenceEngineering.objects.get(project=project)
        # Buat instance formulir view-only, diisi dengan data dari instance IE
        intelligence_engineering_form = IntelligenceEngineeringForm(instance=intelligence_engineering_instance)
        messages.info(request, "Data Rekayasa Kecerdasan (Intelligence Engineering) berhasil diambil dari database lokal.")
    except IntelligenceEngineering.DoesNotExist:
        messages.warning(request, f"Belum ada data Rekayasa Kecerdasan (Intelligence Engineering) untuk proyek '{project.name}'.")
    except Exception as e:
        messages.error(request, f"Terjadi kesalahan tak terduga saat mengambil data Rekayasa Kecerdasan: {e}")
        logger.error(f"Error fetching IE instance for project {project.id}: {e}", exc_info=True)

    if request.method == 'POST':
        form = ProblemFramingForm(request.POST)
        if form.is_valid():
            problem_framing = form.save(commit=False)
            problem_framing.project = project
            problem_framing.framed_by = request.user
            problem_framing.save()
            messages.success(request, f"Problem Framing untuk proyek '{project.name}' berhasil disimpan!")
            return redirect('projek:problem_framing_list')
        else:
            messages.error(request, "Terjadi kesalahan saat menyimpan Problem Framing. Silakan periksa isian Anda.")
    else:
        initial_data = {
            'problem_description': f"Masalah terkait proyek: '{project.name}'. ({project.description})",
        }
        # Jika Anda ingin mengisi field ProblemFraming dari data IE, lakukan di sini
        # if intelligence_engineering_form and intelligence_engineering_form.instance:
        #     initial_data['some_problem_field'] = intelligence_engineering_form.instance.mo_organizational

        form = ProblemFramingForm(initial=initial_data)

    context = {
        'form': form, # Ini adalah ProblemFramingForm yang bisa diedit
        'project': project,
        'page_title': f"Problem Framing untuk Proyek: {project.name}",
        'intelligence_engineering_form': intelligence_engineering_form, # <-- Lewatkan form read-only ini ke template
    }
    return render(request, 'problem_framing/create_problem_framing.html', context)

@login_required
def problem_framing_list_view(request):
    problem_framings = ProblemFraming.objects.all().order_by('-created_at')

    # --- Tambahan untuk Fitur Search ---
    query = request.GET.get('q') # Dapatkan nilai dari parameter 'q' di URL (query string)
    if query:
        # Filter ProblemFraming berdasarkan 'problem_description' atau 'target_goal'
        # Menggunakan Q objects memungkinkan Anda melakukan OR lookups
        # icontains adalah case-insensitive containment test
        from django.db.models import Q
        problem_framings = problem_framings.filter(
            Q(problem_description__icontains=query) |
            Q(target_goal__icontains=query) |
            Q(project__name__icontains=query) # Anda juga bisa mencari berdasarkan nama proyek
        ).distinct() # Gunakan distinct() untuk menghindari duplikasi jika ada multiple matches

    context = {
        'problem_framings': problem_framings,
        'page_title': 'Daftar Problem Framing',
        'query': query, # Kirim query kembali ke template agar search bar tetap terisi
    }
    return render(request, 'problem_framing/problem_framing_list.html', context)

@login_required
def edit_problem_framing_view(request, pk):
    problem_framing = get_object_or_404(ProblemFraming, pk=pk) # Ambil ProblemFraming berdasarkan PK-nya
    project = problem_framing.project # Ambil proyek terkait dari ProblemFraming

    intelligence_engineering_form = None # Inisialisasi awal

    try:
        intelligence_engineering_instance = IntelligenceEngineering.objects.get(project=project)
        intelligence_engineering_form = IntelligenceEngineeringForm(instance=intelligence_engineering_instance)
        messages.info(request, "Data Rekayasa Kecerdasan (Intelligence Engineering) berhasil diambil dari database lokal.")
    except IntelligenceEngineering.DoesNotExist:
        messages.warning(request, f"Belum ada data Rekayasa Kecerdasan (Intelligence Engineering) untuk proyek '{project.name}'.")
    except Exception as e:
        messages.error(request, f"Terjadi kesalahan tak terduga saat mengambil data Rekayasa Kecerdasan: {e}")
        logger.error(f"Error fetching IE instance for project {project.id}: {e}", exc_info=True)

    if request.method == 'POST':
        form = ProblemFramingForm(request.POST, instance=problem_framing)
        if form.is_valid():
            form.save()
            messages.success(request, f"Problem Framing untuk proyek '{project.name}' berhasil diperbarui!")
            return redirect('projek:problem_framing_list')
        else:
            messages.error(request, "Terjadi kesalahan saat memperbarui Problem Framing.")
    else:
        form = ProblemFramingForm(instance=problem_framing)

    context = {
        'form': form, # Ini adalah ProblemFramingForm yang bisa diedit
        'project': project, # Kirim objek proyek ke template jika diperlukan
        'page_title': f"Edit Problem Framing: {project.name}",
        'intelligence_engineering_form': intelligence_engineering_form, # <-- Lewatkan form read-only ini ke template
    }
    return render(request, 'problem_framing/create_problem_framing.html', context)

@login_required
# Menerima PK dari ProblemFraming, bukan Project ID
def delete_problem_framing_view(request, pk):
    problem_framing = get_object_or_404(ProblemFraming, pk=pk) # Ambil ProblemFraming berdasarkan PK-nya
    project = problem_framing.project # Ambil proyek terkait dari ProblemFraming

    if request.method == 'POST':
        problem_framing.delete()
        messages.success(request, f"Problem Framing untuk proyek '{project.name}' berhasil dihapus.")
        return redirect('projek:problem_framing_list')
    else:
        # Untuk permintaan GET, render halaman konfirmasi
        context = {
            'project': project,
            'problem_framing': problem_framing,
            'page_title': f"Hapus Problem Framing: {project.name}"
        }
        return render(request, 'problem_framing/confirm_delete_problem_framing.html', context)

@login_required
def problem_framing_detail_view(request, pk):
    problem_framing = get_object_or_404(ProblemFraming, pk=pk)
    project = problem_framing.project

    intelligence_engineering_form = None # Inisialisasi awal

    try:
        intelligence_engineering_instance = IntelligenceEngineering.objects.get(project=project)

        # --- PERBAIKAN UTAMA DI SINI ---
        # Gunakan nama kelas, bukan nama variabel yang sedang diinisialisasi
        intelligence_engineering_form = IntelligenceEngineeringForm(instance=intelligence_engineering_instance)

        messages.info(request, "Data Rekayasa Kecerdasan (Intelligence Engineering) berhasil diambil.")
    except IntelligenceEngineering.DoesNotExist:
        messages.warning(request, f"Belum ada data Rekayasa Kecerdasan (Intelligence Engineering) untuk proyek '{project.name}'.")
        logger.warning(f"IE data not found for project ID {project.id} ({project.name}) when viewing Problem Framing detail.")
    except Exception as e:
        messages.error(request, f"Terjadi kesalahan tak terduga saat mengambil data Rekayasa Kecerdasan: {e}. Cek log server.")
        logger.error(f"Error fetching IE instance or creating IE form for project {project.id}: {e}", exc_info=True)

    context = {
        'problem_framing': problem_framing,
        'project': project,
        'intelligence_engineering_form': intelligence_engineering_form,
        'page_title': f"Detail Problem Framing: {problem_framing.project.name}"
    }
    return render(request, 'problem_framing/problem_framing_detail.html', context)
#---REQUEST DATASETS----

@login_required
def select_project_for_dataset_request_view(request):
    projects = Project.objects.all().order_by('name') # Anda bisa filter proyek jika perlu
    context = {
        'projects': projects,
        'page_title': 'Pilih Proyek untuk Permintaan Dataset'
    }
    return render(request, 'request_dataset/select_project_for_dataset_request.html', context)

@login_required
def create_dataset_request_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = DatasetRequestForm(request.POST)
        if form.is_valid():
            dataset_request = form.save(commit=False)
            dataset_request.project = project
            dataset_request.requested_by = request.user
            dataset_request.save()

            messages.success(request, f"Permintaan dataset untuk proyek '{project.name}' berhasil disimpan!")

            return redirect('projek:dataset_request_list') # Arahkan ke daftar permintaan dataset
        else:
            messages.error(request, "Terjadi kesalahan saat menyimpan permintaan dataset. Silakan periksa isian Anda.")
    else:
        initial_data = {
            'description_problem': f"Dataset dibutuhkan untuk analisis atau pengembangan AI terkait proyek: '{project.name}'. ({project.description})",
            'start_date_needed': project.start_date,
        }
        form = DatasetRequestForm(initial=initial_data)

    context = {
        'form': form,
        'project': project,
        'page_title': f"Buat Permintaan Dataset untuk Proyek: {project.name}"
    }
    return render(request, 'request_dataset/create_dataset_request.html', context)

@login_required
def dataset_request_list_view(request):
    dataset_requests = DatasetRequest.objects.all().order_by('-created_at')
    context = {
        'dataset_requests': dataset_requests,
        'page_title': 'Daftar Permintaan Dataset'
    }
    return render(request, 'request_dataset/dataset_request_list.html', context)

@login_required
def delete_request_dataset(request, request_id):
    dataset_request_obj = get_object_or_404(DatasetRequest, id=request_id)
    project_name = dataset_request_obj.project.name if dataset_request_obj.project else "proyek tidak dikenal"

    if request.method == 'POST':
        dataset_request_obj.delete()
        messages.success(request, f"Permintaan dataset untuk proyek '{project_name}' berhasil dihapus.")
        return redirect('projek:dataset_request_list')
    else:
        context = {
            'dataset_request': dataset_request_obj, # Kirim objek dataset_request ke template
            'page_title': f"Hapus Permintaan Dataset: {project_name}"
        }
        return render(request, 'request_dataset/confirm_delete_request_dataset.html', context)




@login_required
def datasets(request):
    api_url = "https://undirty.pythonanywhere.com/api/dataset-reply/" # URL API terbaru
    saved_count = 0
    skipped_count = 0

    try:
        response = requests.get(api_url, timeout=10) # Tambahkan timeout
        response.raise_for_status()
        external_dataset_replies = response.json()

        if not isinstance(external_dataset_replies, list):
            logger.warning("[Dataset Sync] External Dataset API did not return a list. Assuming single object and wrapping in a list.")
            external_dataset_replies = [external_dataset_replies]

        logger.info(f"[Dataset Sync] Received {len(external_dataset_replies)} dataset replies from external API.")

        for item in external_dataset_replies:
            project_name_from_api = item.get('project_name')
            message_text_from_api = item.get('message_text')
            link_text_from_api = item.get('dataset_link')
            created_at_str_from_api = item.get('created_at')

            if not project_name_from_api or not message_text_from_api:
                logger.warning(f"[Dataset Sync] Skipping DatasetReply: Missing 'project_name' or 'message_text'. Data: {item}")
                skipped_count += 1
                messages.warning(request, "Beberapa balasan dataset dilewati karena data tidak lengkap.")
                continue

            try:
                project_obj = Project.objects.get(name=project_name_from_api)
                created_at_dt = None
                if created_at_str_from_api:
                    try:
                        created_at_dt = datetime.fromisoformat(created_at_str_from_api.replace('Z', '+00:00'))
                    except ValueError:
                        logger.warning(f"[Dataset Sync] Invalid 'created_at' format from API for project '{project_name_from_api}': {created_at_str_from_api}. Using current time.")

                dataset_reply_obj, created = DatasetReply.objects.update_or_create(
                    project=project_obj,
                    message=message_text_from_api, # Menggunakan message sebagai kunci unik sederhana. Pertimbangkan external_reply_id jika ada untuk keunikan lebih baik.
                    defaults={
                        'created_at': created_at_dt if created_at_dt else datetime.now(),
                        'dataset_link': link_text_from_api, # Menyimpan link ke field model
                    }
                )
                if created:
                    logger.info(f"[Dataset Sync] New DatasetReply created for project '{project_name_from_api}'.")
                else:
                    logger.info(f"[Dataset Sync] DatasetReply updated for project '{project_name_from_api}'.")
                saved_count += 1
            except Project.DoesNotExist:
                logger.warning(f"[Dataset Sync] Project '{project_name_from_api}' not found in local DB for this DatasetReply. Skipped.")
                messages.warning(request, f"Balasan dataset untuk proyek '{project_name_from_api}' tidak dapat disimpan karena proyek tidak ditemukan secara lokal. Silakan sinkronkan proyek terlebih dahulu.")
                skipped_count += 1
            except Exception as e:
                logger.error(f"[Dataset Sync] Unexpected error saving DatasetReply for project '{project_name_from_api}': {e}", exc_info=True)
                messages.error(request, f"Gagal menyimpan balasan dataset untuk proyek '{project_name_from_api}': {e}")
                skipped_count += 1

        if saved_count > 0:
            messages.success(request, f"Berhasil menyimpan/memperbarui {saved_count} balasan dataset.")
        if skipped_count > 0:
            messages.info(request, f"Sebanyak {skipped_count} balasan dataset dilewati.")

    except requests.exceptions.RequestException as e:
        logger.error(f"[Dataset Sync] Error fetching data from API: {e}", exc_info=True)
        messages.error(request, f"Gagal memuat data dataset dari API eksternal: Kesalahan koneksi atau respons tidak valid.")
    except ValueError as e:
        logger.error(f"[Dataset Sync] Error parsing JSON from API: {e}", exc_info=True)
        messages.error(request, f"Respons API eksternal tidak valid (bukan JSON): {e}")
    except Exception as e:
        logger.error(f"[Dataset Sync] An unexpected error occurred in datasets function: {e}", exc_info=True)
        messages.error(request, f"Terjadi kesalahan tak terduga saat memproses dataset: {e}")

    final_dataset_replies_for_template = DatasetReply.objects.all().order_by('-created_at')

    context = {
        'page_title': "Daftar Balasan Dataset",
        'dataset_replies': final_dataset_replies_for_template, # Mengirimkan objek DatasetReply ke template
    }
    return render(request, 'datasets/list_dataset.html', context) # Nama template mungkin perlu disesuaikan


#------- INTELLIGENCE ENGINEERING ----------
@login_required
def select_project_for_intelligence_engineering_view(request):
    # Hanya tampilkan proyek yang belum memiliki entri IntelligenceEngineering
    projects_for_ie = Project.objects.filter(intelligence_engineering__isnull=True).order_by('name')
    context = {
        'projects': projects_for_ie,
        'page_title': 'Pilih Proyek untuk Rekayasa Kecerdasan'
    }
    return render(request, 'intelligence_engineering/select_project_ie.html', context)

#---DATA PROCESSINGG-----
@login_required
def select_project_for_data_processing_view(request):
    projects = Project.objects.all().order_by('name')
    context = {
        'projects': projects,
        'page_title': 'Pilih Proyek untuk Pemrosesan Data'
    }
    return render(request, 'data_processing/select_project_for_data_processing.html', context)

@login_required
def create_data_processing_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = DataProcessingForm(request.POST, request.FILES)
        if form.is_valid():
            data_processing = form.save(commit=False)
            data_processing.project = project
            data_processing.save()
            messages.success(request, f"Entri Pemrosesan & Pelatihan Data untuk proyek '{project.name}' berhasil dibuat!")
            return redirect('projek:data_processing_list_view')
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Terjadi kesalahan saat membuat entri Pemrosesan & Pelatihan Data. Silakan periksa isian Anda.")
    else:
        form = DataProcessingForm(initial={'project': project})

    context = {
        'form': form,
        'project': project,
        'page_title': f"Buat Entri Pemrosesan & Pelatihan Data untuk Proyek: {project.name}"
    }
    return render(request, 'data_processing/create_data_processing.html', context)

@login_required
def data_processing_list_view(request):
    data_processings = DataProcessing.objects.all().order_by('-created_at')
    context = {
        'data_processings': data_processings,
        'page_title': 'Daftar Pemrosesan Data'
    }
    return render(request, 'data_processing/data_processing_list.html', context)


@login_required
def edit_data_processing_view(request, pk):
    data_processing = get_object_or_404(DataProcessing, pk=pk)
    if request.method == 'POST':
        form = DataProcessingForm(request.POST, request.FILES, instance=data_processing)
        if form.is_valid():
            form.save()
            messages.success(request, f"Entri Pemrosesan Data untuk proyek '{data_processing.project.name}' berhasil diperbarui!")
            return redirect('projek:data_processing_list_view')
        else:
            messages.error(request, "Terjadi kesalahan saat memperbarui entri Pemrosesan Data.")
    else:
        form = DataProcessingForm(instance=data_processing)

    context = {
        'form': form,
        'data_processing': data_processing,
        'page_title': f"Edit Pemrosesan Data: {data_processing.project.name}"
    }
    return render(request, 'data_processing/create_data_processing.html', context)

@login_required
def delete_processing_data(request, pk):
    # First, get the DataProcessing object using the PK from the URL
    data_processing = get_object_or_404(DataProcessing, pk=pk)

    # Then, get the associated project from the data_processing object
    project = data_processing.project # <-- CORRECTED LINE HERE!

    if request.method == 'POST':
        data_processing.delete()
        messages.success(request, f"Data Processing untuk proyek '{project.name}' berhasil dihapus.")
        return redirect('projek:data_processing_list_view')
    else:
        # For GET requests, render a confirmation page
        context = {
            'project': project, # Still pass project for display
            'data_processing': data_processing,
            'page_title': f"Hapus Data Processing: {project.name}"
        }
        return render(request, 'data_processing/confirm_delete_data_processing.html', context)

@login_required
def data_processing_detail_view(request, pk):
    data_processing = get_object_or_404(DataProcessing, pk=pk)
    context = {
        'data_processing': data_processing,
        'page_title': f"Detail Pemrosesan Data: {data_processing.project.name}"
    }
    return render(request, 'data_processing/data_processing_detail.html', context)


# --- TRAINING MODELS -----
@login_required
def select_project_for_training_model_view(request):
    projects = Project.objects.all().order_by('name')
    context = {
        'projects': projects,
        'page_title': 'Pilih Proyek untuk Pelatihan Model'
    }
    return render(request, 'model_training/select_project_for_model_training.html', context)

@login_required
def create_training_model_view(request, pk):
    project = get_object_or_404(Project, id=pk)

    if request.method == 'POST':
        form = TrainingModelForm(request.POST, request.FILES, project_instance=project)
        if form.is_valid():
            training_model = form.save(commit=False)
            training_model.project = project
            training_model.trained_by = request.user
            training_model.save()
            messages.success(request, f"Entri Pelatihan Model untuk proyek '{project.name}' berhasil dibuat!")
            return redirect('projek:model_training_list') # Pastikan nama URL sesuai di urls.py
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Terjadi kesalahan saat membuat entri Pelatihan Model. Silakan periksa isian Anda.")
    else:
        form = TrainingModelForm(project_instance=project)

    context = {
        'form': form,
        'project': project,
        'page_title': f"Buat Entri Pelatihan Model untuk Proyek: {project.name}"
    }
    return render(request, 'model_training/create_model_training.html', context)

@login_required
def training_model_list_view(request):
    training_models = TrainingModel.objects.all().order_by('-training_date')
    context = {
        'training_models': training_models,
        'page_title': 'Daftar Pelatihan Model'
    }
    return render(request, 'model_training/model_training_list.html', context)

@login_required
def edit_training_model_view(request, pk):
    training_model = get_object_or_404(TrainingModel, pk=pk)
    if request.method == 'POST':
        form = TrainingModelForm(request.POST, request.FILES, instance=training_model)
        if form.is_valid():
            form.save()
            messages.success(request, f"Entri Pelatihan Model untuk proyek '{training_model.project.name}' berhasil diperbarui!")
            return redirect('projek:model_training_list')
        else:
            messages.error(request, "Terjadi kesalahan saat memperbarui entri Pelatihan Model.")
    else:
        form = TrainingModelForm(instance=training_model)

    context = {
        'form': form,
        'training_model': training_model,
        'page_title': f"Edit Pelatihan Model: {training_model.model_name}"
    }
    return render(request, 'model_training/create_model_training.html', context) # Gunakan template create untuk edit

@login_required
def training_model_detail_view(request, pk):
    training_model = get_object_or_404(TrainingModel, pk=pk)
    context = {
        'training_model': training_model,
        'page_title': f"Detail Pelatihan Model: {training_model.model_name}"
    }
    return render(request, 'model_training/model_training_detail.html', context)

@login_required
def delete_training_model(request, pk):
    project = get_object_or_404(Project, id=pk)
    training_model = get_object_or_404(TrainingModel, pk=pk)

    if request.method == 'POST':
        training_model.delete()
        messages.success(request, f"Training Model untuk proyek '{project.name}' berhasil dihapus.")
        return redirect('projek:model_training_list')
    else:
        # For GET requests, render a confirmation page
        context = {
            'project': project,
            'training_model': training_model,
            'page_title': f"Hapus Training Model: {project.name}"
        }
        return render(request, 'model_training/confirm_delete_training_model.html', context)

# --- api content ---
@login_required
def api_content_settings_view(request):
    """
    Menampilkan daftar API yang tersedia, membedakan antara internal dan eksternal.
    """
    api_list = [
        # --- Internal APIs ---
        {
            'name': 'Project API',
            'description': 'Mengelola informasi dasar proyek, termasuk nama, deskripsi, lokasi, dan status.',
            'models': 'Project',
            'endpoints': {
                'ListCreate': '/api-content/projects/', # Endpoint List/Create
            },
            'is_external': False # Flag untuk API internal
        },
        {
            'name': 'Problem Framing API',
            'description': 'Mengelola definisi masalah dan tujuan proyek untuk solusi AI, termasuk konteks data dan fitur kunci.',
            'models': 'ProblemFraming',
            'endpoints': {
                'ListCreate': '/api-content/problem-framings/', # Endpoint List/Create
            },
            'is_external': False
        },
        {
            'name': 'Dataset Request API',
            'description': 'Mengelola permintaan dataset dari proyek, termasuk deskripsi kebutuhan data, format, dan estimasi ukuran.',
            'models': 'DatasetRequest',
            'endpoints': {
                'ListCreate': '/api-content/dataset-requests/', # Endpoint List/Create
            },
            'is_external': False
        },
        {
            'name': 'Data Processing API',
            'description': 'Menyimpan detail aktivitas pemrosesan data, sumber data, langkah-langkah pembersihan, dan rekayasa fitur.',
            'models': 'DataProcessing',
            'endpoints': {
                'ListCreate': '/api-content/data-processings/', # Endpoint List/Create
            },
            'is_external': False
        },
        {
            'name': 'Training Model API',
            'description': 'Mengelola informasi model AI yang dilatih, termasuk tipe model, algoritma, performa, dan strategi penyempurnaan.',
            'models': 'TrainingModel',
            'endpoints': {
                'ListCreate': '/api-content/training-models/', # Endpoint List/Create
            },
            'is_external': False
        },
        {
            'name': 'Sent Project IC Status API',
            'description': 'Menyediakan daftar proyek dengan ID, nama, dan statusnya. Dirancang untuk konsumsi oleh sistem manajemen proyek eksternal.',
            'models': 'Project',
            'endpoints': {
                'List': '/api-content/project-statuses/', # Ini adalah API internal yang Anda sediakan (hanya List)
            },
            'is_external': False
        },
        # --- External APIs ---
        {
            'name': 'Project Management (External) API', # Menggunakan nama yang lebih jelas
            'description': 'API ini dikonsumsi dari sistem manajemen proyek eksternal, menyediakan data proyek yang disinkronkan ke dalam sistem ini.',
            'models': 'Projects (External)',
            'endpoints': {
                'List': settings.EXTERNAL_PROJECT_MENEJ_API_URL, # Menggunakan URL langsung dari settings
            },
            'is_external': True # Flag untuk API eksternal
        },
        {
            'name': 'Intelligence Engineering (External) API',
            'description': 'API ini dikonsumsi dari sistem eksternal (tim rekayasa kecerdasan), menyediakan data detail rekayasa kecerdasan. Data disinkronkan ke dalam sistem ini.',
            'models': 'IntelligenceEngineering (External)',
            'endpoints': {
                'List': settings.EXTERNAL_PROJECT_ENGINEER_API_URL,
            },
            'is_external': True # Flag untuk API eksternal
        },
    ]

    context = {
        'page_title': 'Pengaturan Konten API',
        'api_list': api_list,
    }
    return render(request, 'api-content/api-list.html', context)

#---DOCUMENTATIONS-----

@login_required
def documentations(request):
    projects = Project.objects.all().order_by('name')
    context = {
        'projects': projects,
        'page_title': 'Pilih Proyek untuk Dokumentasi Lengkap'
    }
    return render(request, 'documentations/documentation.html', context)


@login_required
def generate_project_documentation_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    problem_framing = None
    try:
        problem_framing = project.problem_framing
    except ProblemFraming.DoesNotExist:
        messages.info(request, "Tidak ada Problem Framing ditemukan untuk proyek ini.")

    data_processings = DataProcessing.objects.filter(project=project).order_by('-created_at')
    training_models = TrainingModel.objects.filter(project=project).order_by('-training_date')
    dataset_replies = DatasetReply.objects.filter(project=project).order_by('-created_at')
    documents = Document.objects.filter(project=project).order_by('-created_at')

    intelligence_engineering = None
    try:
        intelligence_engineering = project.intelligence_engineering
    except IntelligenceEngineering.DoesNotExist:
        messages.info(request, "Tidak ada Intelligence Engineering ditemukan untuk proyek ini.")

    context = {
        'page_title': f"Dokumentasi Proyek: {project.name}",
        'project': project,
        'problem_framing': problem_framing,
        'data_processings': data_processings,
        'training_models': training_models,
        'dataset_replies': dataset_replies,
        'documents': documents,
        'intelligence_engineering': intelligence_engineering,
    }
    return render(request, 'documentations/project_documentation.html', context)


#--api intelligence-creations--
