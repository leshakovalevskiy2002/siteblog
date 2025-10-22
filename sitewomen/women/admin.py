from django.contrib import admin, messages
from django.db.models import Count, Q
from django.db.models.functions import Length
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from django_mptt_admin.admin import DjangoMpttAdmin

from .models import Women, Category, TagPost, Husband, Comment, Rating


class ContentFilter(admin.SimpleListFilter):
    title = _("Sort by articles")
    parameter_name = 'content'

    def lookups(self, request, model_admin):
        return [
            ("short", _("Short articles")),
            ("middle", _("Medium articles")),
            ("long", _("Long articles"))
        ]

    def queryset(self, request, queryset):
        queryset = queryset.annotate(length=Length("content"))
        if self.value() == "short":
            return queryset.filter(length__lt=800)
        if self.value() == "middle":
            return queryset.filter(length__range=(800, 1999))
        if self.value() == "long":
            return queryset.filter(length__gte=2000)


class MarriedFilter(admin.SimpleListFilter):
    parameter_name = "status"
    title = _("Women's marital status")

    def lookups(self, request, model_admin):
        return [
            ("single", _("Single")),
            ("married", _("Married")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "single":
            return queryset.filter(husband=None)
        if self.value() == "married":
            return queryset.filter(~Q(husband=None))


class AgeFilter(admin.SimpleListFilter):
    title = _("Age groups")
    parameter_name = "age_status"

    def lookups(self, request, model_admin):
        return [
            ("young", _("Young age")),
            ("average", _("Middle age")),
            ("elderly", _("Elderly age")),
            ("senile", _("Senile age")),
            ("longevity", _("Longevity"))
        ]

    def queryset(self, request, queryset):
        if self.value() == "young":
            return queryset.filter(age__range=(18, 44))
        if self.value() == "average":
            return queryset.filter(age__range=(45, 59))
        if self.value() == "elderly":
            return queryset.filter(age__range=(60, 74))
        if self.value() == "senile":
            return queryset.filter(age__range=(75, 90))
        if self.value() == "longevity":
            return queryset.filter(age__gt=90)


@admin.register(Women)
class WomenAdmin(admin.ModelAdmin):
    fields = ("title", "slug", "content", "photo", "post_photo",  "cat", "husband", "tags", "author")
    readonly_fields = ("post_photo", )
    prepopulated_fields = {"slug": ("title", )}
    filter_horizontal = ("tags", )
    list_display = ("title", "time_create", "post_photo", "is_published", "cat", "brief_info")
    list_display_links = ("title", )
    ordering = ("-time_create", "title")
    list_editable = ("is_published", )
    list_per_page = 5
    actions = ("set_published", "set_draft")
    search_fields = ("title__startswith", "cat__name")
    list_filter = ("cat__name", "is_published", MarriedFilter, ContentFilter)
    save_on_top = True

    @admin.display(description=_("Brief description"), ordering=Length("content"))
    def brief_info(self, women: Women):
        count = len(women.content)
        return ngettext(
            "Description of %(count)d character",
            "Description of %(count)d characters",
            count
        ) % {'count': count}

    @admin.display(description=_("Image"))
    def post_photo(self, women: Women):
        if women.thumbnail:
            return mark_safe(f"<img src='{women.thumbnail.url}' width=50>")
        return _("No photo")

    @admin.action(description=_("Publish selected entries"))
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Women.Status.PUBLISHED)
        message = ngettext(
            "%(count)d entry was updated",
            "%(count)d entries were updated",
            count
        ) % {'count': count}
        self.message_user(request, message=message)

    @admin.action(description=_("Mark selected entries as draft"))
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Women.Status.DRAFT)
        message = ngettext(
            "%(count)d entry was unpublished",
            "%(count)d entries were unpublished",
            count
        ) % {'count': count}
        self.message_user(request, message=message, level=messages.WARNING)


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    list_display = ("name", "count_women_by_category",)
    list_display_links = ("name", )
    search_fields = ("name", )
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(nums=Count("where_posts",
                    filter=Q(where_posts__is_published=Women.Status.PUBLISHED))).filter(nums__gt=0)
        return queryset

    @admin.display(description=_("Number of women per category"), ordering="nums")
    def count_women_by_category(self, cat):
        return cat.nums


@admin.register(TagPost)
class TagsAdmin(admin.ModelAdmin):
    readonly_fields = ("slug", )
    search_fields = ("tag", )


@admin.register(Husband)
class HusbandAdmin(admin.ModelAdmin):
    fields = ("name", "age")
    list_display = ("name", "age")
    search_fields = ("name", )
    list_filter = (AgeFilter, )


@admin.register(Comment)
class CommentAdminPage(DjangoMpttAdmin):
    list_display = ['author', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    pass