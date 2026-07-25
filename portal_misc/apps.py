from django.apps import AppConfig


class PortalMiscConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portal_misc'

    def ready(self):
        import portal_misc.signals  # noqa: F401 — connects post_save signal for CompanyBankDetails
