from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, logout, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfileForm, ProjectForm, ProblemFramingForm, DatasetRequestForm, UserUpdateForm, IntelligenceEngineeringForm, DataProcessingForm, TrainingModelForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Project, ProblemFraming, DatasetRequest, Profile, IntelligenceEngineering, TrainingModel, DataProcessing

# Create your views here.
def landing_page(request):
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
            form.save()
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
    projects = Project.objects.all().order_by('-created_at') # Urutkan berdasarkan tanggal terbaru
    context = {
        'page_title': 'Dashboard Utama',
        'projects': projects, # Mengirim daftar proyek ke template
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
    # Periksa apakah proyek ini sudah memiliki Problem Framing
    if hasattr(project, 'problem_framing') and project.problem_framing:
        messages.warning(request, f"Proyek '{project.name}' sudah memiliki entri Problem Framing. Silakan edit jika perlu.")
        return redirect('projek:edit_problem_framing', pk=project.problem_framing.pk) # Arahkan ke edit dengan ID ProblemFraming

    if request.method == 'POST':
        form = ProblemFramingForm(request.POST)
        if form.is_valid():
            problem_framing = form.save(commit=False)
            problem_framing.project = project # Kaitkan dengan proyek yang dipilih
            problem_framing.framed_by = request.user # User yang membuat framing
            problem_framing.save()
            messages.success(request, f"Problem Framing untuk proyek '{project.name}' berhasil disimpan!")
            return redirect('projek:problem_framing_list')
        else:
            messages.error(request, "Terjadi kesalahan saat menyimpan Problem Framing. Silakan periksa isian Anda.")
    else:
        initial_data = {
            'problem_description': f"Masalah terkait proyek: '{project.name}'. ({project.description})",
        }
        form = ProblemFramingForm(initial=initial_data)

    context = {
        'form': form,
        'project': project,
        'page_title': f"Problem Framing untuk Proyek: {project.name}"
    }
    return render(request, 'problem_framing/create_problem_framing.html', context)

@login_required
def problem_framing_list_view(request):
    problem_framings = ProblemFraming.objects.all().order_by('-created_at')
    context = {
        'problem_framings': problem_framings,
        'page_title': 'Daftar Problem Framing'
    }
    return render(request, 'problem_framing/problem_framing_list.html', context)

@login_required
# Menerima PK dari ProblemFraming, bukan Project ID
def edit_problem_framing_view(request, pk): 
    problem_framing = get_object_or_404(ProblemFraming, pk=pk) # Ambil ProblemFraming berdasarkan PK-nya
    project = problem_framing.project # Ambil proyek terkait dari ProblemFraming

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
        'form': form,
        'project': project, # Kirim objek proyek ke template jika diperlukan
        'page_title': f"Edit Problem Framing: {project.name}"
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
# Menerima PK dari ProblemFraming, bukan Project ID
def problem_framing_detail_view(request, pk): 
    problem_framing = get_object_or_404(ProblemFraming, pk=pk) # Ambil ProblemFraming berdasarkan PK-nya
    context = {
        'problem_framing': problem_framing,
        'page_title': f"Detail Problem Framing: {problem_framing.project.name}" # Perbaikan judul
    }
    return render(request, 'problem_framing/problem_framing_detail.html', context)

# API PROBLEM FRAMING
#--data request APIS
def problem_framing_api(request, pk):
    try:
        projek = ProblemFraming.objects.get(pk=pk)
        data = {
            'Proyek Terkait': projek.project,
            'Deskripsi Masalah': projek.problem_description,
            'Target / Tujuan (Goal)': projek.target_goal,
            'Stock (Kondisi/Ketersediaan Awal)': projek.stock_initial_state,
            'Input Inflow': projek.input_inflow_description,
            'Output Outflow': projek.output_outflow_description,
            'Fitur Kunci / Data yang Diperlukan': projek.key_features_data,
            'Di-frame oleh': projek.framed_by,

            
            'start_date_needed': projek.created_at.strftime('%Y-%m-%d'),
            'updated_at': projek.updated_at.strftime('%Y-%m-%d'),
        }
        return JsonResponse(data)
    except DatasetRequest.DoesNotExist:
        return JsonResponse({'error': 'Problem Framing Datas not found'}, status=404)




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
            dataset_request.project = project # Kaitkan dengan proyek
            dataset_request.requested_by = request.user # User yang membuat permintaan
            dataset_request.save()
            messages.success(request, f"Permintaan dataset untuk proyek '{project.name}' berhasil dikirim!")
            return redirect('projek:dataset_request_list') # Arahkan ke daftar permintaan
        else:
            messages.error(request, "Terjadi kesalahan saat mengirim permintaan dataset. Silakan periksa isian Anda.")
    else:
        # Anda bisa mengisi awal deskripsi masalah dataset dari deskripsi proyek
        initial_data = {
            'description_problem': f"Dataset dibutuhkan untuk analisis atau pengembangan AI terkait proyek: '{project.name}'. ({project.description})",
            'start_date_needed': project.start_date, # Bisa mengambil tanggal mulai proyek
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
    """
    Menampilkan daftar semua permintaan dataset.
    """
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
        # UBAH INI: Nama URL yang benar adalah 'dataset_request_list'
        return redirect('projek:dataset_request_list')
    else:
        # Untuk permintaan GET, tampilkan halaman konfirmasi
        context = {
            'dataset_request': dataset_request_obj, # Kirim objek dataset_request ke template
            'page_title': f"Hapus Permintaan Dataset: {project_name}"
        }
        return render(request, 'request_dataset/confirm_delete_request_dataset.html', context)


#--data request APIS
def get_request_data_api(request, projek_id):
    try:
        projek = DatasetRequest.objects.get(pk=projek_id)
        data = {
            'deskripsi_problem': projek.deskripsi_problem,
            'target_for_dataset': projek.target_for_dataset,
            'type_data_needed': projek.type_data_needed,
            'num_features': projek.num_features,
            'dataset_size': projek.dataset_size,
            'file_format': projek.file_format,
            'status': projek.status,
            'requested_by': projek.requested_by,

            
            'start_date_needed': projek.start_date_needed.strftime('%Y-%m-%d') if projek.start_date_needed else '',
            'end_date_needed': projek.end_date_needed.strftime('%Y-%m-%d') if projek.end_date_needed else '',
        }
        return JsonResponse(data)
    except DatasetRequest.DoesNotExist:
        return JsonResponse({'error': 'Data entry not found'}, status=404)


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

@login_required
def create_intelligence_engineering_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Periksa apakah proyek ini sudah memiliki Intelligence Engineering
    if hasattr(project, 'intelligence_engineering') and project.intelligence_engineering:
        messages.warning(request, f"Proyek '{project.name}' sudah memiliki entri Rekayasa Kecerdasan. Silakan edit jika perlu.")
        return redirect('projek:edit_intelligence_engineering', project_id=project.id)

    if request.method == 'POST':
        form = IntelligenceEngineeringForm(request.POST)
        if form.is_valid():
            ie_instance = form.save(commit=False)
            ie_instance.project = project
            ie_instance.save()
            messages.success(request, f"Rekayasa Kecerdasan untuk proyek '{project.name}' berhasil disimpan!")
            return redirect('projek:intelligence_engineering_list')
        else:
            messages.error(request, "Terjadi kesalahan saat menyimpan Rekayasa Kecerdasan. Silakan periksa isian Anda.")
    else:
        # Anda bisa mengisi awal beberapa field berdasarkan proyek atau Problem Framing
        initial_data = {
            'project': project.id, # Set nilai awal untuk project FK
            # 'organization_objective': project.description, # Contoh pre-fill
            # ...
        }
        form = IntelligenceEngineeringForm(initial=initial_data)

    context = {
        'form': form,
        'project': project,
        'page_title': f"Buat Rekayasa Kecerdasan untuk Proyek: {project.name}"
    }
    return render(request, 'intelligence_engineering/create_intelligence_engineering.html', context)

@login_required
def intelligence_engineering_list_view(request):
    intelligence_engineerings = IntelligenceEngineering.objects.all().order_by('-created_at')
    context = {
        'intelligence_engineerings': intelligence_engineerings,
        'page_title': 'Daftar Rekayasa Kecerdasan'
    }
    return render(request, 'intelligence_engineering/intelligence_engineering_list.html', context)

@login_required
def edit_intelligence_engineering_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    ie_instance = get_object_or_404(IntelligenceEngineering, project=project)

    if request.method == 'POST':
        form = IntelligenceEngineeringForm(request.POST, instance=ie_instance)
        if form.is_valid():
            form.save()
            messages.success(request, f"Rekayasa Kecerdasan untuk proyek '{project.name}' berhasil diperbarui!")
            return redirect('projek:intelligence_engineering_list')
        else:
            messages.error(request, "Terjadi kesalahan saat memperbarui Rekayasa Kecerdasan.")
    else:
        form = IntelligenceEngineeringForm(instance=ie_instance)

    context = {
        'form': form,
        'project': project,
        'page_title': f"Edit Rekayasa Kecerdasan: {project.name}"
    }
    return render(request, 'intelligence_engineering/create_intelligence_engineering.html', context)


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
        form = DataProcessingForm(request.POST, request.FILES) # Tambahkan request.FILES untuk upload file
        if form.is_valid():
            data_processing = form.save(commit=False)
            data_processing.project = project
            data_processing.processed_by = request.user
            data_processing.save()
            messages.success(request, f"Entri Pemrosesan Data untuk proyek '{project.name}' berhasil dibuat!")
            return redirect('projek:data_processing_list_view')
        else:
            messages.error(request, "Terjadi kesalahan saat membuat entri Pemrosesan Data. Silakan periksa isian Anda.")
    else:
        form = DataProcessingForm()

    context = {
        'form': form,
        'project': project,
        'page_title': f"Buat Entri Pemrosesan Data untuk Proyek: {project.name}"
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
            return redirect('projek:data_processing_list')
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
    project = get_object_or_404(Project, id=pk)
    data_processing = get_object_or_404(DataProcessing, pk=pk) 

    if request.method == 'POST':
        data_processing.delete()
        messages.success(request, f"Data Processing untuk proyek '{project.name}' berhasil dihapus.")
        return redirect('projek:data_processing_list_view')
    else:
        # For GET requests, render a confirmation page
        context = {
            'project': project,
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
        form = TrainingModelForm(request.POST)
        if form.is_valid():
            training_model = form.save(commit=False)
            training_model.project = project
            training_model.trained_by = request.user
            training_model.save()
            messages.success(request, f"Entri Pelatihan Model untuk proyek '{project.name}' berhasil dibuat!")
            return redirect('projek:model_training_list') # Pastikan nama URL sesuai di urls.py
        else:
            messages.error(request, "Terjadi kesalahan saat membuat entri Pelatihan Model. Silakan periksa isian Anda.")
    else:
        form = TrainingModelForm()

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
        form = TrainingModelForm(request.POST, instance=training_model)
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





#---DOCUMENTATIONS-----
def documentations(request):
    return render(request, 'documentations/documentation.html')


#--api intelligence-creations--
