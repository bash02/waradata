from django.apps import AppConfig


class paymentgatewayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paymentGateway'

    def ready(self) -> None:
        import paymentGateway.signals.handlers
