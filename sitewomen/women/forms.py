from captcha.fields import CaptchaField
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Women, Comment


class AddPostForm(forms.ModelForm):
    is_published = forms.BooleanField(required=False, initial=True, label=_("Status"),
                        widget=forms.CheckboxInput(attrs={"class": "form-check-input px-0"}))

    class Meta:
        model = Women
        fields = ["title", "content", "photo", "is_published", "cat", "husband", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control w-25'}),
            "content": forms.Textarea(attrs={"class": 'form-control w-50', "rows": 5}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control w-50"}),
            "cat": forms.Select(attrs={"class": "form-select form-select-sm w-25"}),
            "husband": forms.Select(attrs={"class": "form-select form-select-sm w-25"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select w-25"})
        }
        error_messages = {
            "title": {
                "required": _("Title is required")
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["husband"].empty_label = _("Not married")
        self.fields["cat"].empty_label = _("Select category")


class ContactForm(forms.Form):
    name = forms.CharField(label=_("Your name"), widget=forms.TextInput(attrs={"class": "form-control w-25"}))
    email = forms.EmailField(label=_("Your email"), widget=forms.EmailInput(attrs={"class": "form-control w-25"}),
                             initial="example@mail.ru")
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control w-50', "rows": 5}),
                              label=_("Your comment"))
    captcha = CaptchaField(label=_("Are you human?"))


class CommentForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)
    body = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 5, 'placeholder': _("Enter your comment"), 'class': 'form-control w-50'}))

    class Meta:
        model = Comment
        fields = ["body"]


class SearchForm(forms.Form):
    query = forms.CharField(label=_("Enter search query"),
                    widget=forms.TextInput(attrs={"class": "form-control me-2", "placeholder": _("Search...")}))