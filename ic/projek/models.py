from django.contrib.auth.models import User
from django.db import models
from django.conf import settings 
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    til = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

# Sinyal untuk membuat Profile secara otomatis saat User baru dibuat
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Sinyal untuk menyimpan Profile secara otomatis saat User disimpan
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
class Project(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nama Proyek")
    description = models.TextField(verbose_name="Deskripsi Proyek")
    location = models.CharField(max_length=255, verbose_name="Lokasi")
    start_date = models.DateField(verbose_name="Tanggal Mulai")
    end_date = models.DateField(verbose_name="Tanggal Selesai")
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_projects', verbose_name="Supervisor")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending', verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-start_date'] # Urutkan proyek dari yang terbaru
        verbose_name = "Proyek"
        verbose_name_plural = "Proyek"

class IntelligenceEngineering(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='intelligence_engineering', verbose_name="Proyek Terkait")

    # Bagian 1: Meaningful Objectives (Tujuan Bermakna)
    organization_objective = models.TextField(
        verbose_name="Tujuan Organisasi", 
        help_text="Apa tujuan strategis atau hasil bisnis yang ingin dicapai organisasi dengan implementasi AI ini?"
    )
    leading_indicator = models.TextField(
        verbose_name="Indikator Utama (Leading Indicator)", 
        help_text="Metrik atau sinyal awal apa yang dapat mengindikasikan kemajuan menuju tujuan organisasi?"
    )
    user_outcome = models.TextField(
        verbose_name="Hasil yang Diinginkan Pengguna (User Outcome)", 
        help_text="Apa perubahan positif yang diharapkan pengguna akhir setelah berinteraksi dengan sistem cerdas?"
    )
    model_properties = models.TextField(
        verbose_name="Properti Model yang Diinginkan", 
        help_text="Karakteristik kunci apa yang harus dimiliki model AI (misal: akurasi tinggi, dapat diinterpretasi, skalabilitas, ketahanan)?"
    )

    # Bagian 2: Intelligence Experiences (Pengalaman Kecerdasan)
    automate = models.TextField(
        verbose_name="Otomatisasi", 
        help_text="Bagian mana dari proses atau keputusan yang dapat diotomatisasi oleh sistem cerdas?"
    )
    prompt = models.TextField(
        verbose_name="Pemicu / Pemberian Informasi (Prompt)", 
        help_text="Bagaimana sistem akan meminta atau menerima input dari pengguna atau sistem lain untuk menghasilkan kecerdasan?"
    )
    annotate = models.TextField(
        verbose_name="Anotasi / Pelabelan Data", 
        help_text="Bagaimana data akan diberi label atau dianotasi untuk melatih atau memvalidasi model AI?"
    )
    organization_of_intelligence = models.TextField( # Ganti 'organization' untuk menghindari konflik
        verbose_name="Organisasi Kecerdasan", 
        help_text="Bagaimana 'kecerdasan' (misal: rekomendasi, prediksi) akan diorganisasikan atau disajikan kepada pengguna?"
    )
    system_objective = models.TextField(
        verbose_name="Tujuan Sistem (System Objective)", 
        help_text="Apa tujuan spesifik dari sistem AI yang dirancang (misal: memprediksi churn pelanggan, merekomendasikan produk)?"
    )
    minimize_flaws = models.TextField(
        verbose_name="Meminimalkan Kekurangan/Bias", 
        help_text="Strategi apa yang akan diterapkan untuk mengurangi bias atau kekurangan dalam data atau model?"
    )
    create_data = models.TextField(
        verbose_name="Strategi Pembuatan Data", 
        help_text="Bagaimana data yang dibutuhkan akan dikumpulkan, dihasilkan, atau diperoleh?"
    )

    # Bagian 3: Intelligence Implementations (Implementasi Kecerdasan)
    business_process = models.TextField(
        verbose_name="Integrasi Proses Bisnis", 
        help_text="Bagaimana sistem cerdas akan diintegrasikan ke dalam alur kerja dan proses bisnis yang ada?"
    )
    technology = models.TextField(
        verbose_name="Teknologi yang Digunakan", 
        help_text="Daftar teknologi, framework, atau platform utama yang akan digunakan (misal: TensorFlow, PyTorch, Azure ML, AWS SageMaker)?"
    )
    build_process = models.TextField(
        verbose_name="Proses Pengembangan/Pembangunan", 
        help_text="Langkah-langkah atau metodologi yang akan diikuti dalam membangun dan melatih model AI."
    )

    development_constraints = models.TextField( # Ganti 'batasan_pengembang'
        verbose_name="Batasan Pengembangan", 
        help_text="Kendala teknis, sumber daya, atau waktu yang perlu diperhatikan selama pengembangan."
    )

    realization_status = models.TextField( # Ganti 'status_realisasi'
        verbose_name="Status Realisasi", 
        help_text="Status saat ini dari implementasi atau realisasi proyek kecerdasan ini."
    )

    # Bagian 4: Perencanaan (Planning)
    deployment = models.TextField(
        verbose_name="Rencana Deployment (Penerapan)", 
        help_text="Bagaimana model atau sistem AI akan disebarkan ke lingkungan produksi?"
    )
    maintenance = models.TextField(
        verbose_name="Rencana Pemeliharaan", 
        help_text="Bagaimana sistem AI akan dipelihara dan diperbarui pasca-deployment?"
    )
    operating_system_environment = models.TextField( # Lebih spesifik
        verbose_name="Lingkungan Sistem Operasi", 
        help_text="Sistem operasi atau lingkungan komputasi yang akan digunakan untuk menjalankan sistem cerdas."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Intelligence Engineering for {self.project.name}"

    class Meta:
        verbose_name = "Rekayasa Kecerdasan"
        verbose_name_plural = "Rekayasa Kecerdasan"
        ordering = ['-created_at'] # Urutkan berdasarkan waktu pembuatan terbaru



class ProblemFraming(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='problem_framing', verbose_name="Proyek Terkait")

    # Core Problem Definition
    problem_description = models.TextField(verbose_name="Deskripsi Masalah (Problem Statement)", help_text="Jelaskan masalah bisnis yang ingin diselesaikan.")
    target_goal = models.TextField(verbose_name="Target / Tujuan (Goal)", help_text="Apa yang ingin dicapai secara terukur dengan solusi cerdas?")

    # Data & System Context (Opsional, sesuaikan kebutuhan)
    stock_initial_state = models.TextField(blank=True, null=True, verbose_name="Stock (Kondisi/Ketersediaan Awal)", help_text="Deskripsikan kondisi awal entitas yang relevan dengan masalah (misal: jumlah inventory saat ini).")
    input_inflow_description = models.TextField(blank=True, null=True, verbose_name="Input Inflow", help_text="Data/informasi apa yang masuk dan memengaruhi masalah? (misal: data transaksi, harga pasar, pesanan baru).")
    output_outflow_description = models.TextField(blank=True, null=True, verbose_name="Output Outflow", help_text="Hasil atau efek apa yang diharapkan dari sistem cerdas? (misal: rekomendasi, prediksi penjualan, deteksi anomali).")

    # Features / Data Kunci
    key_features_data = models.TextField(verbose_name="Fitur Kunci / Data yang Diperlukan", help_text="Variabel atau atribut data apa yang penting untuk model sistem cerdas?")

    # Audit Trail
    framed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='framed_problems', verbose_name="Di-frame oleh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Problem Framing for {self.project.name}"

    class Meta:
        verbose_name = "Problem Framing"
        verbose_name_plural = "Problem Framing"
        ordering = ['-created_at']

class DatasetRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('InProgress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    FORMAT_CHOICES = [
        ('CSV', 'CSV'),
        ('JSON', 'JSON'),
        ('SQL', 'SQL Dump'),
        ('Excel', 'Excel (XLSX)'),
        ('Other', 'Lainnya'),
    ]

    # Foreign Key ke Project
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='dataset_requests', verbose_name="Proyek Terkait")

    # Informasi Permintaan Dataset
    description_problem = models.TextField(verbose_name="Deskripsi Masalah (Kebutuhan Dataset)", help_text="Jelaskan masalah atau konteks yang membutuhkan dataset ini.")
    target_for_dataset = models.TextField(verbose_name="Target / Tujuan (Penggunaan Dataset)", help_text="Untuk tujuan apa dataset ini akan digunakan?")
    type_data_needed = models.CharField(max_length=100, verbose_name="Tipe Data yang Dibutuhkan", help_text="Contoh: Data Transaksi, Data Sensor, Data Pelanggan, dll.")
    data_processing_activity = models.TextField(verbose_name="Aktivitas Pemrosesan Data yang Diinginkan", help_text="Deskripsikan pemrosesan awal yang dibutuhkan (misal: filtering, aggregation, anonymization).")
    
    num_features = models.IntegerField(blank=True, null=True, verbose_name="Estimasi Jumlah Fitur", help_text="Estimasi kolom data yang dibutuhkan.")
    dataset_size = models.CharField(max_length=100, blank=True, null=True, verbose_name="Estimasi Ukuran Dataset", help_text="Contoh: 100GB, 1 Juta Baris, dll.")
    file_format = models.CharField(max_length=50, choices=FORMAT_CHOICES, verbose_name="Format File yang Diinginkan")
    
    start_date_needed = models.DateField(verbose_name="Tanggal Mulai Dibutuhkan")
    end_date_needed = models.DateField(verbose_name="Tanggal Selesai Dibutuhkan", blank=True, null=True, help_text="Tanggal batas akhir data yang dibutuhkan (jika historis).")
    
    # Status dan Audit
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending', verbose_name="Status Permintaan")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='requested_datasets', verbose_name="Diminta Oleh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Permintaan Dataset untuk Proyek: {self.project.name} ({self.status})"

    class Meta:
        verbose_name = "Permintaan Dataset"
        verbose_name_plural = "Permintaan Dataset"
        ordering = ['-created_at']

# Data Processing Model
class DataProcessing(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='data_processings', verbose_name="Proyek Terkait")
    
    # Tahap Pemrosesan Data
    data_source = models.TextField(verbose_name="Sumber Data", help_text="Dari mana data diperoleh (misal: Database SQL, API Eksternal, File CSV)?")
    cleaning_steps = models.TextField(verbose_name="Langkah Pembersihan Data", help_text="Deskripsikan langkah-langkah pembersihan (misal: penanganan missing values, duplikasi, outliers).")
    transformation_steps = models.TextField(verbose_name="Langkah Transformasi Data", help_text="Deskripsikan transformasi yang dilakukan (misal: normalisasi, standarisasi, one-hot encoding).")
    feature_engineering = models.TextField(blank=True, null=True, verbose_name="Rekayasa Fitur", help_text="Jika ada, jelaskan fitur baru yang dibuat dari data mentah.")
    data_quality_metrics = models.TextField(blank=True, null=True, verbose_name="Metrik Kualitas Data", help_text="Metrik apa yang digunakan untuk menilai kualitas data setelah pemrosesan?")
    processed_data_location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Lokasi Data yang Diproses", help_text="Path atau lokasi penyimpanan data yang sudah diproses.")
    
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_datasets', verbose_name="Diproses Oleh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pemrosesan Data untuk Proyek: {self.project.name}"

    class Meta:
        verbose_name = "Pemrosesan Data"
        verbose_name_plural = "Pemrosesan Data"
        ordering = ['-created_at']

# Training Model
class TrainingModel(models.Model):
    MODEL_TYPE_CHOICES = [
        ('Classification', 'Klasifikasi'),
        ('Regression', 'Regresi'),
        ('Clustering', 'Klastering'),
        ('Recommendation', 'Rekomendasi'),
        ('NLP', 'Natural Language Processing'),
        ('ComputerVision', 'Computer Vision'),
        ('Other', 'Lainnya'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='trained_models', verbose_name="Proyek Terkait")
    
    model_name = models.CharField(max_length=200, verbose_name="Nama Model")
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES, verbose_name="Tipe Model")
    algorithm_used = models.CharField(max_length=200, verbose_name="Algoritma yang Digunakan", help_text="Contoh: Random Forest, XGBoost, BERT, ResNet.")
    hyperparameters = models.TextField(blank=True, null=True, verbose_name="Hyperparameter", help_text="Detail hyperparameter yang digunakan (dalam format JSON atau teks bebas).")
    training_data_used = models.ForeignKey(DataProcessing, on_delete=models.SET_NULL, null=True, blank=True, related_name='trained_models_from_data', verbose_name="Data Pelatihan yang Digunakan")
    
    evaluation_metrics = models.TextField(verbose_name="Metrik Evaluasi", help_text="Metrik performa model (misal: Akurasi, Presisi, Recall, F1-score, RMSE, MAE, R-squared).")
    model_performance = models.TextField(verbose_name="Performa Model", help_text="Nilai spesifik dari metrik evaluasi (misal: Akurasi: 0.92, F1-score: 0.88).")
    
    trained_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='trained_models_by_user', verbose_name="Dilatih Oleh")
    training_date = models.DateField(auto_now_add=True, verbose_name="Tanggal Pelatihan")
    model_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="Path Model Tersimpan", help_text="Lokasi penyimpanan file model yang sudah dilatih.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pelatihan Model: {self.model_name} untuk Proyek: {self.project.name}"

    class Meta:
        verbose_name = "Pelatihan Model"
        verbose_name_plural = "Pelatihan Model"
        ordering = ['-training_date']