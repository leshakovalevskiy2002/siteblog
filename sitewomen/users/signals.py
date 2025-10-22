from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=get_user_model())
def add_permission_and_token(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)
        content_type = ContentType.objects.get(app_label='auth', model='permission')
        change_psw_perm, flag = Permission.objects.get_or_create(codename='change_psw_perm',
                          defaults={"codename": "change_psw_perm",
                                    "name": "Can change password",
                                    "content_type": content_type
                                    })
        create_post_perm = Permission.objects.get(codename="add_women")
        instance.user_permissions.add(change_psw_perm, create_post_perm)