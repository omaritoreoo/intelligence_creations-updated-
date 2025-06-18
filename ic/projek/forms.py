from django import forms
from django.contrib.auth.models import User
from .models import Profile, ProblemFraming, Project, DatasetRequest, IntelligenceEngineering, DataProcessing, TrainingModel
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from django.core.exceptions import ValidationError # Import ValidationError

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'til']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ceritakan tentang diri Anda...'}),
            'til': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell me something I dont know...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('profile_picture', css_class='form-control-file'),
            Field('bio', css_class='form-control'),
            Field('til', css_class='form-control'),
        )

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nama Pengguna'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nama Depan'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nama Belakang'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Alamat Email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('first_name', css_class='form-control'),
            Field('last_name', css_class='form-control'),
            Field('email', css_class='form-control'),
        )

        self.user = kwargs.get('instance')
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.user and self.user.username != username:
            if User.objects.filter(username=username).exists():
                raise ValidationError("Username ini sudah digunakan oleh pengguna lain. Mohon pilih username yang berbeda.")
            return username


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name',
            'description',
            'location',
            'start_date',
            'end_date',
            'supervisor',
            'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Deskripsi lengkap proyek'}),
            'location': forms.TextInput(attrs={'placeholder': 'Lokasi proyek (misal: Jakarta, Head Office)'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class IntelligenceEngineeringForm(forms.ModelForm):
    class Meta:
        model = IntelligenceEngineering
        fields = '__all__'
        widgets = {
            # Pastikan nama field di sini sesuai dengan nama field di model IntelligenceEngineering Anda.
            # Berdasarkan model yang Anda berikan sebelumnya, field-nya adalah:
            'mo_organizational': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'mo_leading_indicators': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'mo_user_outcomes': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'mo_model_properties': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'ie_automate': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'ie_prompt': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'ie_annotate': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'ie_organization': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'ie_system_objectives': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'ie_minimize_flaws': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'ie_create_data': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'ii_business_process': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'ii_technology': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'ii_build_process': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'bd_limitation': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'sr_realization': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'pr_deployment': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'pr_maintenance': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'pr_operating': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
        }


class ProblemFramingForm(forms.ModelForm):
    class Meta:
        model = ProblemFraming
        fields = [
            'problem_description',
            'target_goal',
            'stock_initial_state',
            'input_inflow_description',
            'output_outflow_description',
            'key_features_data',

        ]
        widgets = {
            'problem_description': forms.Textarea(attrs={'rows': 5}),
            'target_goal': forms.Textarea(attrs={'rows': 3}),
            'stock_initial_state': forms.Textarea(attrs={'rows': 3}),
            'input_inflow_description': forms.Textarea(attrs={'rows': 3}),
            'output_outflow_description': forms.Textarea(attrs={'rows': 3}),
            'key_features_data': forms.Textarea(attrs={'rows': 4}),
        }

class DatasetRequestForm(forms.ModelForm):
    class Meta:
        model = DatasetRequest
        fields = [
            'description_problem',
            'target_for_dataset',
            'type_data_needed',
            'data_processing_activity',
            'num_features',
            'dataset_size',
            'file_format',
            'start_date_needed',
            'end_date_needed',
        ]
        widgets = {
            'description_problem': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Jelaskan masalah atau konteks yang membutuhkan dataset ini.'}),
            'target_for_dataset': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Contoh: Untuk melatih model prediksi penjualan, untuk analisis pasar.'}),
            'type_data_needed': forms.TextInput(attrs={'placeholder': 'Contoh: Data Transaksi Penjualan, Data Sensor Suhu, Data Log Server.'}),
            'data_processing_activity': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Contoh: Filter data tahun 2023-2024, agregasi per bulan, anonimisasi PII.'}),
            'num_features': forms.NumberInput(attrs={'placeholder': 'Estimasi jumlah kolom (misal: 20)'}),
            'dataset_size': forms.TextInput(attrs={'placeholder': 'Contoh: 500 MB, 1 Juta Baris, 2 GB.'}),
            'start_date_needed': forms.DateInput(attrs={'type': 'date'}),
            'end_date_needed': forms.DateInput(attrs={'type': 'date'}),
        }

# --- DataProcessingForm (YANG SUDAH DIUBAH) ---
class DataProcessingForm(forms.ModelForm):
    class Meta:
        model = DataProcessing
        fields = [
            'project', # Tetap di sini agar bisa diinisialisasi
            'data_source_description',
            'processing_steps_summary',
            'feature_engineering_details',
            'processed_data_location',
            'processed_file',
            'status',
            # 'processed_by' akan diisi di view, tidak perlu di form
        ]
        widgets = {
            'project': forms.HiddenInput(), # Menyembunyikan field project dari user
            'data_source_description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Misal: Data dari Database Penjualan, File Excel Hasil Survei Pelanggan'}),
            'processing_steps_summary': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Ringkasan langkah pembersihan (duplikat, nilai hilang) dan transformasi (normalisasi, agregasi).'}),
            'feature_engineering_details': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Jelaskan bagaimana fitur-fitur baru dibuat dari data mentah.'}),
            'processed_data_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Path atau URL penyimpanan data yang sudah diproses.'}),
            'processed_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'data_source_description': 'Deskripsi Sumber Data',
            'processing_steps_summary': 'Ringkasan Pembersihan & Transformasi',
            'feature_engineering_details': 'Detail Rekayasa Fitur',
            'processed_data_location': 'Lokasi File Data Diproses',
            'processed_file': 'File Data Diproses (CSV/lainnya)',
            'status': 'Status Pemrosesan',
        }

    def __init__(self, *args, **kwargs):
        # Ambil project instance jika diberikan (untuk initial value hidden field)
        project_instance = kwargs.pop('project_instance', None)
        super().__init__(*args, **kwargs)

        # Set initial value untuk field 'project' jika ada project_instance
        if project_instance:
            self.fields['project'].initial = project_instance
            # Opsional: Jika Anda ingin memastikan project tidak bisa diubah bahkan dari inspeksi elemen,
            # Anda bisa membuatnya readonly, meski hiddenInput sudah cukup.
            # self.fields['project'].widget.attrs['readonly'] = True

        # Tambahkan kelas form-control ke semua field yang tersisa secara dinamis
        for field_name, field in self.fields.items():
            if field_name not in ['project', 'processed_file']: # Skip hidden dan file input
                if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Textarea, forms.Select, forms.DateInput, forms.DateTimeInput)):
                    field.widget.attrs.update({'class': 'form-control'})

class TrainingModelForm(forms.ModelForm):
    class Meta:
        model = TrainingModel
        fields = [
            'project',
            'model_name',
            'model_type',
            'algorithm_used',
            'training_data_used',
            'model_performance',
            'model_path', # Ini adalah FileField dari models.py
            'refining_strategy',
            'refining_status',
            'refined_performance',
        ]
        widgets = {
            'project': forms.HiddenInput(),
            'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Misal: Model Prediksi Churn v1'}),
            'model_type': forms.Select(attrs={'class': 'form-control'}),
            'algorithm_used': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Misal: Random Forest, Neural Network'}),
            'training_data_used': forms.Select(attrs={'class': 'form-control'}),
            'model_performance': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': '{"accuracy": 0.89, "f1_score": 0.85} (format JSON)'}),
            
            # --- WIDGET INI SUDAH BENAR UNTUK FileField ---
            'model_path': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            # -----------------------------------------------
            
            'refining_strategy': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Jelaskan strategi untuk meningkatkan performa model (misal: Hyperparameter tuning).'}),
            'refining_status': forms.Select(attrs={'class': 'form-control'}),
            'refined_performance': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': '{"accuracy": 0.91, "rmse": 0.5} (format JSON, jika ada refining)'}),
        }
        labels = {
            'model_name': 'Nama Model',
            'model_type': 'Tipe Model',
            'algorithm_used': 'Algoritma Digunakan',
            'training_data_used': 'Data Pelatihan Digunakan',
            'model_performance': 'Performa Model (JSON)',
            'model_path': 'File Model Terlatih', # Label yang lebih sesuai
            'refining_strategy': 'Strategi Penyempurnaan',
            'refining_status': 'Status Penyempurnaan',
            'refined_performance': 'Performa Setelah Penyempurnaan (JSON)',
        }

    def __init__(self, *args, **kwargs):
        project_instance = kwargs.pop('project_instance', None)
        super().__init__(*args, **kwargs)

        if project_instance:
            self.fields['project'].initial = project_instance
            self.fields['training_data_used'].queryset = DataProcessing.objects.filter(project=project_instance)
        elif self.instance and self.instance.project:
            self.fields['training_data_used'].queryset = DataProcessing.objects.filter(project=self.instance.project)
        else:
            self.fields['training_data_used'].queryset = DataProcessing.objects.all()

        for field_name, field in self.fields.items():
            # Pastikan 'model_path' dikecualikan dari penambahan kelas 'form-control' default
            if field_name not in ['project', 'model_path']: 
                if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Textarea, forms.Select, forms.DateInput, forms.DateTimeInput)):
                    field.widget.attrs.update({'class': 'form-control'})
