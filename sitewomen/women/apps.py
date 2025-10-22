from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WomenConfig(AppConfig):
    verbose_name = _("Famous Women of the World")
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'women'
