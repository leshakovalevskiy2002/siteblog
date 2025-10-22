from django import template
from django.db.models import Count
from django.urls import reverse
from django.utils import translation
from django.utils import timezone

from women.models import TagPost, Women, Category, PageVisit

register = template.Library()


@register.inclusion_tag("women/list_categories.html")
def show_categories(cat_selected=0):
    categories = Category.objects.all()
    return {"categories": categories, "cat_selected": cat_selected}


@register.inclusion_tag("women/list_tags.html")
def show_tags():
    tags = TagPost.objects.filter(tags__is_published=Women.Status.PUBLISHED).annotate(
                                        total=Count("tags")).filter(total__gt=0)
    return {"tags": tags}


@register.inclusion_tag("women/users_rating.html")
def show_users_rating(post, ip):
    rating = post.ratings.filter(ip_address=ip)
    if rating:
        value = rating[0].value
    else:
        value = None
    return {"value": value, "p": post}


@register.simple_tag
def change_language_url(request, language_code):
    current_language = translation.get_language()

    resolver = getattr(request, 'resolver_match', None)
    if not resolver:
        return request.get_full_path()

    route_name = resolver.url_name
    args = request.resolver_match.args
    kwargs = request.resolver_match.kwargs
    namespace = request.resolver_match.namespace
    if namespace:
        route_name = f"{namespace}:{route_name}"

    request.route_name = route_name
    translation.activate(language_code)
    path = reverse(request.route_name, args=args, kwargs=kwargs)
    params = "&".join([f"{key}={value}" for key, value in request.GET.items()])
    if params:
        path = f"{path}?{params}"
    translation.activate(current_language)
    return path


@register.simple_tag
def get_page_count_views(url):
    now = timezone.localtime(timezone.now()).day
    pages = PageVisit.objects.filter(url=url, visit_time__day=now).aggregate(
                                    count=Count("visit_time__day"))
    return pages["count"]