from django.utils.translation import gettext_lazy as _
from django.urls import path

from . import views


urlpatterns = [
    path("", views.home_view, name="chat_home"),
    path(_("groups/<uuid:uuid>/"), views.group_chat_view, name="group")
]