from django.contrib.postgres.search import TrigramSimilarity, TrigramWordSimilarity
from django.db.models import Prefetch, ExpressionWrapper, FloatField
from django.views.generic.base import ContextMixin
from django.urls import resolve

from .models import TagPost
from .forms import SearchForm


class DataMixin(ContextMixin):
    extra_context = {}
    title = None
    paginate_by = 3
    template_name = 'women/content.html'

    def __init__(self):
        if self.title is not None:
            self.extra_context["title"] = self.title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "cat_selected" not in context:
            context["cat_selected"] = None
        if "paginator" in context:
            context["elided_page_range"] = context["paginator"].get_elided_page_range(
                        context["page_obj"].number, on_each_side=2, on_ends=1)
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        context["ip"] = x_forwarded_for.split(',')[0] if x_forwarded_for else self.request.META.get('REMOTE_ADDR')
        return context

    def get_template_names(self):
        if self.request.headers.get('Hx-Request'):
            return ['women/content.html']
        return [self.template_name]


class SearchFieldMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("query")
        context["query"] = query
        context["search_form"] = SearchForm(self.request.GET) if query else SearchForm()
        resolved = resolve(self.request.path_info)
        context["route_name"] = resolved.url_name
        return context

    @staticmethod
    def calculate_similarity(query, queryset):
        if query:
            A = 1.0
            B = 0.4
            total = A + B

            queryset = queryset.annotate(
                similarity=ExpressionWrapper(
                    (A / total * TrigramSimilarity('title', query)) +
                    (B / total * TrigramWordSimilarity(query, 'content')),
                    output_field=FloatField()
                )
            ).filter(similarity__gte=0.2).order_by('-similarity')

        return queryset.select_related("author", "cat").prefetch_related(
                        Prefetch("tags", TagPost.objects.all()))