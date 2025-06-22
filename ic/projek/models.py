from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import os


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
    external_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    STATUS_CHOICES = [
        ('Ongoing', 'Ongoing'),
        ('Stop', 'Stop'),
        ('Done', 'Done'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nama Proyek")
    description = models.TextField(verbose_name="Deskripsi Proyek")
    location = models.CharField(max_length=255, verbose_name="Lokasi")
    start_date = models.DateField(verbose_name="Tanggal Mulai")
    end_date = models.DateField(verbose_name="Tanggal Selesai")
    supervisor = models.CharField(max_length=255, verbose_name="Supervisor Proyek", blank=True, null=True)
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
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='intelligence_engineering')

    external_id_ie = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # Meaningful Objectives (from "meaningful_objectives" in JSON)
    mo_organizational = models.TextField(blank=True, null=True)
    mo_leading_indicators = models.TextField(blank=True, null=True)
    mo_user_outcomes = models.TextField(blank=True, null=True)
    mo_model_properties = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Intelligence Engineering"
        verbose_name_plural = "Intelligence Engineering Entries"

    def __str__(self):
        return f"IE for Project: {self.project.name}" if self.project else f"IE Entry {self.id}"

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
        ('Ongoing', 'Ongoing'),
        ('Stop', 'Stop'),
        ('Done', 'Done'),
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

class DatasetReply(models.Model):
    external_reply_id = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name="ID Balasan Eksternal")
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='dataset_replies',
        verbose_name="Proyek Terkait"
    )

    dataset_request = models.ForeignKey(
        DatasetRequest,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='replies',
        verbose_name="Permintaan Dataset Terkait"
    )

    message = models.TextField(verbose_name="Pesan Balasan")
    original_sender_email = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Pengirim Asli (Eksternal)"
    )

    dataset_link = models.URLField(verbose_name="URL")
    original_sender_email = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Pengirim Asli (Eksternal)"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Waktu Balasan")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Balasan Dataset"
        verbose_name_plural = "Balasan Dataset"
        # Urutkan berdasarkan waktu pembuatan, yang terbaru di atas.
        ordering = ['-created_at']

    def __str__(self):
        # Representasi yang mudah dibaca.
        return f"Balasan Dataset untuk '{self.project.name}' (ID Eksternal: {self.external_reply_id or 'N/A'})"


# Data Processing Model
class DataProcessing(models.Model):
    # Pilihan Status Pemrosesan
    PROCESSING_STATUS_CHOICES = [
        ('in_progress', 'Dalam Proses'),
        ('completed', 'Selesai'),
        ('failed', 'Gagal'),
    ]

    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='data_processings',
        verbose_name="Proyek Terkait"
    )

    # Deskripsi ringkas aktivitas pemrosesan data
    data_source_description = models.TextField(
        verbose_name="Deskripsi Sumber Data",
        help_text="Misal: 'Data dari Database Penjualan', 'File Excel Hasil Survei Pelanggan'"
    )
    processing_steps_summary = models.TextField(
        verbose_name="Ringkasan Langkah Pembersihan & Transformasi",
        help_text="Catatan ringkas tentang bagaimana data dibersihkan (duplikat, nilai hilang) dan diubah (normalisasi, agregasi).",
        blank=True,
        null=True
    )
    feature_engineering_details = models.TextField(
        verbose_name="Detail Rekayasa Fitur",
        help_text="Bagaimana fitur-fitur baru dibuat dari data mentah untuk model.",
        blank=True,
        null=True
    )

    # Lokasi atau file dari data yang sudah diproses
    processed_data_location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Lokasi File Data Diproses",
        help_text="Path atau URL tempat data yang sudah bersih dan siap pakai disimpan."
    )
    processed_file = models.FileField(
        upload_to='processed_data_files/',
        blank=True,
        null=True,
        verbose_name="File Data Diproses"
    )

    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Diproses Oleh"
    )
    status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='in_progress',
        verbose_name="Status Pemrosesan"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pemrosesan Data untuk {self.project.name} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Pemrosesan Data"
        verbose_name_plural = "Pemrosesan Data"

class TrainingModel(models.Model):
    # Pilihan Tipe Model
    MODEL_TYPE_CHOICES = [
        ('classification', 'Klasifikasi'),
        ('regression', 'Regresi'),
        ('clustering', 'Clustering'),
        ('nlp', 'Natural Language Processing'),
        ('cv', 'Computer Vision'),
        ('other', 'Lain-lain'),
    ]

    # Pilihan Status Penyempurnaan (Refining)
    REFINING_STATUS_CHOICES = [
        ('not_needed', 'Tidak Dibutuhkan'),
        ('in_progress', 'Dalam Proses'),
        ('completed', 'Selesai'),
        ('failed', 'Gagal'),
    ]

    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='training_models',
        verbose_name="Proyek Terkait"
    )

    model_name = models.CharField(
        max_length=100,
        verbose_name="Nama Model"
    )
    model_type = models.CharField(
        max_length=50,
        choices=MODEL_TYPE_CHOICES,
        verbose_name="Tipe Model"
    )
    algorithm_used = models.CharField(
        max_length=100,
        verbose_name="Algoritma Digunakan",
        blank=True,
        null=True # Bisa dikosongkan jika tipe modelnya 'other' dan algoritma tidak spesifik
    )

    # Kaitan dengan DataProcessing (opsional jika ingin melihat data latihannya)
    training_data_used = models.ForeignKey(
        'DataProcessing',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='models_trained_with',
        verbose_name="Data Pelatihan Digunakan"
    )

    # Performa Model, termasuk Akurasi. Gunakan JSONField untuk fleksibilitas metrik lain.
    model_performance = models.JSONField(
        verbose_name="Performa Model",
        help_text="(contoh: {'akurasi': 0.89, 'f1_score': 0.85})"
    )

    # Lokasi penyimpanan file model yang terlatih
    model_path = models.FileField(
        upload_to='trained_models/',
        blank=True,
        null=True,
        verbose_name="Lokasi File Model",
        help_text="Unggah file model yang sudah terlatih (misal: .pkl, .h5, .pt)."
    )

    # Field untuk Penyempurnaan (Refining) Model
    refining_strategy = models.TextField(
        verbose_name="Strategi Penyempurnaan Model",
        help_text="Jelaskan strategi untuk meningkatkan performa model (misal: 'Hyperparameter tuning dengan Grid Search', 'Penambahan data augmentasi').",
        blank=True,
        null=True
    )
    refining_status = models.CharField(
        max_length=20,
        choices=REFINING_STATUS_CHOICES,
        default='not_needed',
        verbose_name="Status Penyempurnaan"
    )

    trained_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Dilatih Oleh"
    )
    training_date = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Pelatihan")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Model: {self.model_name} ({self.project.name})"

    @property
    def model_file_name(self):
        """Mengembalikan hanya nama file dari path model_path."""
        if self.model_path:
            return os.path.basename(self.model_path.name)
        return None

    class Meta:
        verbose_name = "Pelatihan Model"
        verbose_name_plural = "Pelatihan Model"

class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('technical', 'Dokumen Teknis'),
        ('report', 'Laporan'),
        ('other', 'Lain-lain'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Proyek Terkait"
    )
    title = models.CharField(max_length=255, verbose_name="Judul Dokumen")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    file = models.FileField(
        upload_to='project_documents/', # Folder untuk menyimpan file
        verbose_name="File Dokumen"
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        default='other',
        verbose_name="Tipe Dokumen"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='uploaded_documents',
        verbose_name="Diunggah Oleh"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.project.name})"

    class Meta:
        verbose_name = "Dokumen Proyek"
        verbose_name_plural = "Dokumen Proyek"
        ordering = ['-created_at']
