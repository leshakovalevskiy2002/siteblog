from django.contrib.auth.views import (LogoutView, PasswordChangeDoneView,
                                       PasswordResetDoneView, PasswordResetCompleteView)
from django.urls import path
from django.utils.translation import gettext_lazy as _

from users import views


app_name = 'users'

urlpatterns = [
    path(_("login/"), views.LoginUser.as_view(), name="login"),    # users:login
    path(_("logout/"), LogoutView.as_view(), name="logout"),  # users:logout

    path(_("registration/"), views.RegistrationUser.as_view(), name="registration"),
    path(_("registration/confirm_email/"), views.confirm_email, name="confirm_email"),
    path(_("registration/verify_email/<uuid:token>/"), views.verify_email, name="verify_email"),
    path(_("registration_done/"), views.registration_done, name="registration_done"),

    path(_("profile/"), views.UserProfile.as_view(), name="profile"),
    path(_("show_profile/<slug:slug>/"), views.ShowProfile.as_view(), name="show_profile"),

    path(_("password_change/"), views.UserPasswordChangeView.as_view(), name="password_change"),
    path(_("password_change/done/"), PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
                                  name="password_change_done"),

    path(_("password_reset/"), views.UserPasswordResetView.as_view(), name="password_reset"),
    path(_("password_reset/done/"), PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
                                  name="password_reset_done"),
    path(_("password_reset/<uidb64>/<token>/"), views.UserPasswordResetConfirmView.as_view(),
                                  name="password_reset_confirm"),
    path(_("password_reset/complete/"), PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
                                  name="password_reset_complete")
]