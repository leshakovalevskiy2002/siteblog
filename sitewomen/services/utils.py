from uuid import uuid4

def unique_slugify(instance, unique_slug):
    model = instance.__class__
    while model.objects.filter(slug=unique_slug).exclude(pk=instance.pk).exists():
        unique_slug = f'{unique_slug}-{uuid4().hex[:8]}'
    return unique_slug