from django.apps import AppConfig
from django.conf import settings


class AppAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.accounts"

    def ready(self):
        if settings.SCHEDULER_DEFAULT:
            from . import runapscheduler

            runapscheduler.start()
