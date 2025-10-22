from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _


class AuthorRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user == self.get_object().author or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        messages.info(request, _("Only the author can edit or delete this post!"))
        return redirect('home')