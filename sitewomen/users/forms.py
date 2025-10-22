from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       PasswordChangeForm, PasswordResetForm,
                                       SetPasswordForm)
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_("Username or E-mail"), widget=forms.TextInput(attrs={"class": "form-control w-25"}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={"class": "form-control w-25"}))
    remember_me = forms.BooleanField(label=_("Remember me"), required=False,
                        widget=forms.CheckboxInput(attrs={"class": "form-check-input px-0 mt-2"}))
    recaptcha = ReCaptchaField()

    def clean(self):
        try:
            cleaned_data = super().clean()
            return cleaned_data
        except ValidationError as e:
            email = self.cleaned_data["username"]
            if get_user_model().objects.filter(email=email).exists():
                self.add_error(None, _("Please verify your email to log in"))
            else:
                raise e


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'class': 'form-control w-25'}))
    password2 = forms.CharField(label=_("Repeat password"), widget=forms.PasswordInput(attrs={'class': 'form-control w-25'}))

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name"]
        labels = {
            'username': _("Username"),
            "email": _("E-mail")
        }
        widgets = {
            "username": forms.TextInput(attrs={'class': 'form-control w-25'}),
            "email": forms.EmailInput(attrs={"class": "form-control w-25"}),
            "first_name": forms.TextInput(attrs={'class': 'form-control w-25'}),
            "last_name": forms.TextInput(attrs={'class': 'form-control w-25'})
        }

    def clean_email(self):
        email = self.cleaned_data["email"]

        if get_user_model().objects.filter(email=email, email_verified=True).exists():
            reset_url = reverse_lazy('users:password_reset')
            raise ValidationError(mark_safe(
                _("E-mail address %(email)s has already been used to create an account. "
                  "If this account belongs to you but you forgot the password, "
                  "<a href='%(url)s'>try to reset it here</a>.") % {"email": email, "url": reset_url}
            ))

        return email


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label=_("Username"), widget=forms.TextInput(attrs={"class": "form-control w-25"}))
    email = forms.CharField(disabled=True, required=False, label=_("E-mail"), widget=forms.EmailInput(attrs={"class": "form-control w-25"}))
    this_year = datetime.today().year
    date_birth = forms.DateField(label=_("Date of birth"),
            widget=forms.SelectDateWidget(years=tuple(range(this_year - 100, this_year - 5)), attrs={"class": "form-select"}))

    class Meta:
        model = get_user_model()
        fields = ['photo', 'username', 'email', 'date_birth', 'first_name', 'last_name', "description"]
        widgets = {
            'first_name': forms.TextInput(attrs={"class": "form-control w-25"}),
            'last_name': forms.TextInput(attrs={"class": "form-control w-25"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control w-50"}),
            "description": forms.Textarea(attrs={"class": "form-control w-25", "rows": 5}),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput(attrs={"class": "form-control w-25"}))
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput(attrs={"class": "form-control w-25"}))
    new_password2 = forms.CharField(label=_("Confirm password"),
                                    widget=forms.PasswordInput(attrs={"class": "form-control w-25"}))


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_("E-mail address"),widget=forms.EmailInput(
                        attrs={"autocomplete": "email", "class": "form-control w-25"}))


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("New password"), strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control w-25"}))
    new_password2 = forms.CharField(label=_("Confirm new password"), strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control w-25"}))