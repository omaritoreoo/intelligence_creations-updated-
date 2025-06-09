from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projek.models import Profile # Sesuaikan 'projek' dengan nama aplikasi Anda

class Command(BaseCommand):
    help = 'Membuat objek Profil untuk pengguna yang sudah ada yang belum memilikinya.'

    def handle(self, *args, **options):
        User = get_user_model()
        # Cari semua pengguna yang TIDAK memiliki profil
        users_tanpa_profil = User.objects.filter(profile__isnull=True)
        jumlah_dibuat = 0

        self.stdout.write(self.style.SUCCESS(f"Mengecek pengguna yang belum punya profil..."))

        for user in users_tanpa_profil:
            # Buat profil baru untuk pengguna ini
            Profile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f"  > Profil dibuat untuk pengguna: {user.username}"))
            jumlah_dibuat += 1

        if jumlah_dibuat > 0:
            self.stdout.write(self.style.SUCCESS(f"\nBerhasil membuat {jumlah_dibuat} profil baru."))
        else:
            self.stdout.write(self.style.SUCCESS("\nSemua pengguna sudah memiliki profil. Tidak ada yang perlu dibuat."))