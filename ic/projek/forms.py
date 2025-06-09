from django import forms
from django.contrib.auth.models import User
from .models import Profile, ProblemFraming, Project, DatasetRequest, IntelligenceEngineering, DataProcessing, TrainingModel
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from django.core.exceptions import ValidationError # Import ValidationError


class ProfileForm(forms.ModelForm): # Ini adalah form yang sudah Anda berikan
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'til']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ceritakan tentang diri Anda...'}),
            'til': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell me something I dont know...'}), # Placeholder untuk 'til'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('profile_picture', css_class='form-control-file'),
            Field('bio', css_class='form-control'),
            Field('til', css_class='form-control'), # Menambahkan 'til' ke layout
            # Submit button akan ditambahkan secara terpisah di template jika Anda ingin dua form terpisah
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
            # Submit button akan ditambahkan secara terpisah di template jika Anda ingin dua form terpisah
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
        # Tentukan bidang mana dari model Project yang ingin Anda tampilkan di formulir
        fields = [
            'name',
            'description',
            'location',
            'start_date',
            'end_date',
            'supervisor',
            'status'
        ]
        # Widgets untuk kustomisasi tampilan bidang formulir (opsional, tapi disarankan untuk tanggal)
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Deskripsi lengkap proyek'}),
            'location': forms.TextInput(attrs={'placeholder': 'Lokasi proyek (misal: Jakarta, Head Office)'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}), # Penting agar tampil sebagai kalender di browser
            'end_date': forms.DateInput(attrs={'type': 'date'}),   # Penting agar tampil sebagai kalender di browser
        }

class IntelligenceEngineeringForm(forms.ModelForm):
    class Meta:
        model = IntelligenceEngineering
        fields = '__all__' 
        widgets = {
            'organization_objective': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'leading_indicator': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'user_outcome': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'model_properties': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'automate': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'prompt': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'annotate': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'organization_of_intelligence': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'system_objective': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'minimize_flaws': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'create_data': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'business_process': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'technology': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'build_process': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'development_constraints': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'realization_status': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'deployment': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'maintenance': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'operating_system_environment': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
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
        # project dan requested_by akan diisi otomatis di view
        # status juga akan diisi otomatis ke 'Pending'
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

#get dataset (nanti aja)



#data_processing
class DataProcessingForm(forms.ModelForm):
    class Meta:
        model = DataProcessing
        fields = [
            'project', # Mungkin akan disembunyikan atau diisi otomatis di view
            'data_source',
            'cleaning_steps',
            'transformation_steps',
            'feature_engineering',
            'data_quality_metrics',
            'processed_data_location',
            # 'processed_by' akan diisi otomatis di view
        ]
        widgets = {
            'data_source': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Contoh: PostgreSQL database "sales_db", API Google Analytics, file CSV dari S3 bucket.'}),
            'cleaning_steps': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Detail langkah pembersihan data: handle missing values, remove duplicates, etc.'}),
            'transformation_steps': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Detail langkah transformasi data: normalisasi, one-hot encoding, feature scaling.'}),
            'feature_engineering': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Jelaskan fitur baru yang dibuat (misal: rasio penjualan per pelanggan, usia pelanggan).'}),
            'data_quality_metrics': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Contoh: Akurasi data 98%, kelengkapan data 99%, konsistensi data.'}),
            'processed_data_location': forms.TextInput(attrs={'placeholder': 'Path atau URL penyimpanan data yang sudah diproses.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Jika Anda ingin menyembunyikan field 'project' di form (karena diisi di view)
        #self.fields['project'].widget = forms.HiddenInput()

#training model
class TrainingModelForm(forms.ModelForm):
    class Meta:
        model = TrainingModel
        fields = [
            'project', # Mungkin akan disembunyikan atau diisi otomatis di view
            'model_name',
            'model_type',
            'algorithm_used',
            'hyperparameters',
            'training_data_used', # Pilihan dropdown untuk DataProcessing
            'evaluation_metrics',
            'model_performance',
            # 'trained_by' dan 'training_date' akan diisi otomatis
            'model_path',
        ]
        widgets = {
            'model_name': forms.TextInput(attrs={'placeholder': 'Nama unik untuk model ini (misal: Sales_Prediction_v1)'}),
            'algorithm_used': forms.TextInput(attrs={'placeholder': 'Contoh: Logistic Regression, CNN, Decision Tree.'}),
            'hyperparameters': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Contoh: {"learning_rate": 0.01, "epochs": 100, "batch_size": 32}'}),
            'evaluation_metrics': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Contoh: Accuracy, Precision, Recall, F1-score.'}),
            'model_performance': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Contoh: Accuracy: 0.85, F1-score: 0.80, RMSE: 12.5.'}),
            'model_path': forms.TextInput(attrs={'placeholder': 'Lokasi penyimpanan file model (misal: /models/sales_v1.pkl)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter pilihan 'training_data_used' berdasarkan 'project' jika diperlukan
        # Ini akan membutuhkan 'project' instance dilewatkan ke form saat inisialisasi
        if 'project' in self.initial:
            project_instance = self.initial['project']
            self.fields['training_data_used'].queryset = DataProcessing.objects.filter(project=project_instance)
        # Jika Anda ingin menyembunyikan field 'project'
        # self.fields['project'].widget = forms.HiddenInput()