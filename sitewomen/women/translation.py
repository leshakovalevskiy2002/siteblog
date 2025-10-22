from modeltranslation.translator import register, TranslationOptions

from .models import Women, Category, TagPost, Comment


@register(Women)
class PostTranslationOptions(TranslationOptions):
    fields = ('content', )


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', )


@register(TagPost)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('tag', )


@register(Comment)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('body', )