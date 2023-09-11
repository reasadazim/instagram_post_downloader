from django.apps import AppConfig


class InstadownloadappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'instadownloadapp'

    def ready(self):
        from .jobs import updater
        updater.start()