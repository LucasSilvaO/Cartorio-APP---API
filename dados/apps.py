from django.apps import AppConfig


class DadosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dados'

    def ready(self):
        import dados.signals