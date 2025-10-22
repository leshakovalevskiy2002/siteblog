from unidecode import unidecode

from django.core.validators import MinLengthValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager

from .validators import RussianValidator
from services.utils import unique_slugify


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Women.Status.PUBLISHED)


class Women(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, _("Draft")
        PUBLISHED = 1, _("Published")

    title = models.CharField(max_length=255, verbose_name=_("Title"),
                             validators=[
                                 MinLengthValidator(5, message=_("The title is too short")),
                                 RussianValidator()
                             ])
    slug = models.SlugField(max_length=255, db_index=True, verbose_name=_("Slug"))
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", null=True, blank=True,
                              verbose_name=_("Photo"), default="photos/placeholder300.jpg")
    thumbnail = ImageSpecField(
        source='photo',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 80}
    )
    content = RichTextField(config_name='awesome_ckeditor', blank=True, verbose_name=_("Content"))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_("Time create"))
    time_update = models.DateTimeField(auto_now=True, verbose_name=_("Time update"))
    is_published = models.IntegerField(default=Status.PUBLISHED, choices=Status.choices, verbose_name=_("Status"))
    cat = TreeForeignKey("Category", on_delete=models.PROTECT, related_name="posts",
                            related_query_name="where_posts", verbose_name=_("Categories"))
    tags = models.ManyToManyField('TagPost', blank=True, related_name="tags", verbose_name=_("Tags"),
                                  related_query_name="tags")
    tags_taggle = TaggableManager()
    husband = models.OneToOneField("Husband", on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="woman", verbose_name=_("Husband"))
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name="posts", null=True,
                               verbose_name=_("Author"))

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Famous women")
        verbose_name_plural = _("Famous women")
        ordering = ["-time_create"]
        get_latest_by = ["time_create"]
        indexes = [
            models.Index(fields=["-time_create"]),
            models.Index(fields=["is_published"], name='is_published_idx')
        ]

    def get_absolute_url(self):
        return reverse("post", args=(self.slug, ))

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, slugify(unidecode(self.title)))
        super().save(*args, **kwargs)

    def get_sum_rating(self):
        return sum([rating.value for rating in self.ratings.all()])


class Category(MPTTModel):
    name = models.CharField(max_length=100, db_index=True, verbose_name=_("Category"))
    slug = models.SlugField(max_length=255, db_index=True, verbose_name=_("Slug"))
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name='children',
        verbose_name=_('Parent category')
    )

    class MPTTMeta:
        order_insertion_by = ('name',)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", args=(self.slug,))
        
    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, slugify(unidecode(self.name)))
        super().save(*args,  **kwargs)


class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True, verbose_name=_("Tag"))
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name=_("Slug"))

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse("tag", args=(self.slug, ))
    
    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.tag))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

class Husband(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    age = models.IntegerField(null=True, verbose_name=_("Age"))
    m_count = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Man")
        verbose_name_plural = _("Men")


class UploadFiles(models.Model):
    image = models.FileField(upload_to="uploads_model", verbose_name=_("Upload an image"))


class Comment(MPTTModel):
    post = models.ForeignKey(Women, on_delete=models.CASCADE, related_name='comments',
                             verbose_name=_("Title of the post"))
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="comments",
                               verbose_name=_("Author"))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children', verbose_name=_("Parent comment"))
    body = models.TextField(verbose_name=_("Comment"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Date of create"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Date of update"))
    active = models.BooleanField(default=True, verbose_name=_("Status"))
    is_updated = models.BooleanField(default=False)

    class MTTMeta:
        order_insertion_by = ('-created',)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ['-created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return _("%(author)s commented on post %(post)s") % {
            "author": self.author.username,
            "post": self.post
        }


class Rating(models.Model):
    post = models.ForeignKey(to=Women, verbose_name=_('Post'), on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(to=get_user_model(), verbose_name=_('User'),
                             on_delete=models.CASCADE, blank=True, null=True)
    value = models.IntegerField(verbose_name=_('Value'), choices=[(1, _('Like')), (-1, _('Dislike'))])
    time_create = models.DateTimeField(verbose_name=_('Time of create'), auto_now_add=True)
    ip_address = models.GenericIPAddressField(verbose_name=_('IP address'))

    class Meta:
        unique_together = ('post', 'ip_address')
        ordering = ('-time_create',)
        indexes = [models.Index(fields=['-time_create', 'value'])]
        verbose_name = _('Rating')
        verbose_name_plural = _('Ratings')

    def __str__(self):
        return self.post.title


class PageVisit(models.Model):
    url = models.CharField(max_length=500)
    visit_time = models.DateTimeField(auto_now_add=True)