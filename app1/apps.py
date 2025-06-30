from django.apps import AppConfig # type: ignore


class App1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app1'

    def ready(self):
        import app1.signals