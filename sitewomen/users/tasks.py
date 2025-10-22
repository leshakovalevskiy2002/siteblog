from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from sitewomen.celery import app


@app.task
def send_verification_email(user_id, link):
    UserModel = get_user_model()
    user = UserModel.objects.get(pk=user_id)
    send_mail(
            _("Confirm your email"),
            _("To confirm your email, please follow this link: %(link)s") % {"link": link},
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True
    )