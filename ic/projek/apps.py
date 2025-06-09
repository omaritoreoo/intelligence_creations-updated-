from django.apps import AppConfig


class ProjekConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projek'

# accounts/apps.py
def ready(self):
    import accounts.signals
