from unidecode import unidecode
import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill

from services.utils import unique_slugify


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        user = super().create_superuser(username, email, password, **extra_fields)
        user.email_verified = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    photo = models.ImageField(upload_to="profile/%Y/%m/%d/", blank=True, null=True, verbose_name=_("Profile picture"),
                              default="profile/anonim.png")
    date_birth = models.DateField(blank=True, null=True, verbose_name=_("Date of birth"))
    thumbnail = ImageSpecField(
        source='photo',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 80}
    )
    description = RichTextField(config_name='awesome_ckeditor', blank=True, verbose_name=_('Description'),
                                max_length=500)
    slug = models.SlugField(max_length=255, verbose_name=_("URL"))

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, unidecode(self.username))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("users:show_profile", args=(self.slug,))

    def __str__(self):
        return self.username

    def is_online(self):
        last_seen = cache.get(f'last-seen-{self.pk}')
        if last_seen is not None and timezone.now() < last_seen + timezone.timedelta(seconds=300):
            return True
        return False