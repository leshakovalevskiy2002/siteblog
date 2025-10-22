from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import EmailMessage
from django.core.cache import cache
from django.forms import ValidationError
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.template.defaultfilters import timesince
from django.views.generic import (View, ListView, DetailView,
                                  FormView, CreateView,
                                  UpdateView, DeleteView,
                                  TemplateView)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _, ngettext, get_language

from .models import Women, TagPost, Category, Comment, PageVisit, Rating
from .forms import AddPostForm, ContactForm, CommentForm
from .utils import DataMixin, SearchFieldMixin
from .tasks import translate_model_content
from services.mixins import AuthorRequiredMixin
from sitewomen import settings


def delete_cache_keys(category: str, tags: list[str]) -> None:
    cache.delete("cached_women_list")
    cache.delete(f"cached_list_by_category_{category}")
    if tags:
        for tag in tags:
            cache.delete(f"cached_list_by_tag_{tag}")


class HomePage(DataMixin, SearchFieldMixin, ListView):
    template_name = "women/index.html"
    context_object_name = 'posts'
    title = _("Home page")
    extra_context = {
        "cat_selected":  0
    }
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get("query")
        queryset = cache.get_or_set("cached_women_list", Women.published.all())
        return self.calculate_similarity(query, queryset)


class About(LoginRequiredMixin, DataMixin, TemplateView):
    template_name = 'women/about.html'
    title = _("About the site")


class ShowPost(DataMixin, DetailView):
    template_name = "women/post.html"
    context_object_name = "post"
    slug_url_kwarg = "post_slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context["post"]
        post_tags = post.tags.all()
        similar_posts = Women.published.filter(tags__in=post_tags).exclude(pk=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-time_update')[:4]
        context["title"] = post.title
        context["cat_selected"] = post.cat.pk
        context["comments"] = post.comments.filter(active=True, parent=None)
        context["form"] = CommentForm()
        context["similar_posts"] = similar_posts
        context["login_url"] = reverse("users:login") + f"?next={post.get_absolute_url()}"
        return context

    def get_object(self, queryset=None):
        self.slug = self.kwargs[self.slug_url_kwarg]
        PageVisit.objects.create(
            url=self.slug
        )
        return get_object_or_404(Women.published, slug=self.slug)


class AddPage(PermissionRequiredMixin, SuccessMessageMixin, DataMixin, CreateView):
    permission_required = "women.add_women"
    template_name = "women/addpage.html"
    form_class = AddPostForm
    success_url = reverse_lazy("home")
    title = _("Add article")
    success_message = _("The post has been successfully added!")

    def form_valid(self, form):
        w = form.save(commit=False)
        w.content_ru = w.content
        w.content_en = w.content
        w.content_be = w.content
        w.author = self.request.user
        w.save()
        translate_model_content.delay("Women", "content", w.pk)
        delete_cache_keys(w.cat.slug, [tag.slug for tag in w.tags.all()])
        return super().form_valid(form)


class UpdatePage(AuthorRequiredMixin, SuccessMessageMixin, DataMixin, UpdateView):
    template_name = "women/edit_page.html"
    model = Women
    form_class = AddPostForm
    success_url = reverse_lazy("home")
    title = _("Edit article")
    success_message = _("The post has been successfully updated!")
    context_object_name = "post"

    def form_valid(self, form):
        w = form.save(commit=False)
        w.content_ru = w.content
        w.content_en = w.content
        w.content_be = w.content
        w.save()
        translate_model_content.delay("Women", "content", w.pk)
        delete_cache_keys(w.cat.slug, [tag.slug for tag in w.tags.all()])
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        current_language = get_language()
        if current_language in ['en', 'be']:
            del form.fields['title']
        return form


class DeletePage(AuthorRequiredMixin, DataMixin, DeleteView):
    template_name = "women/delete_post.html"
    success_url = reverse_lazy("home")
    context_object_name = "post"
    model = Women
    title = _("Delete article")

    def form_valid(self, form):
        delete_cache_keys(self.object.cat.slug, [tag.slug for tag in self.object.tags.all()])
        return super().form_valid(form)


class Contact(LoginRequiredMixin, DataMixin, FormView):
    form_class = ContactForm
    template_name = "women/contact.html"
    title = _("Feedback form")
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        cd = form.cleaned_data
        user = self.request.user
        try:
            if user.email != cd["email"]:
                raise ValidationError(message=_("This is not your email address"))
            EmailMessage(
                _(f"Message from {cd['name']}"),
                _(f"User question - {cd['comment']}"),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],
                reply_to=[cd["email"]]
            ).send()
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error("email", e.message)
            return self.form_invalid(form)


class ShowCategory(DataMixin, SearchFieldMixin, ListView):
    template_name = "women/index.html"
    context_object_name = "posts"
    allow_empty = True

    def get_queryset(self):
        query = self.request.GET.get("query")
        cat_slug = self.kwargs["cat_slug"]
        self.parent_category = Category.objects.get(slug=cat_slug)
        parent_and_descendants = self.parent_category.get_descendants(include_self=True)
        slugs = parent_and_descendants.values_list("slug", flat=True)
        queryset = cache.get_or_set(f"cached_list_by_category_{cat_slug}", Women.published.filter(cat__slug__in=slugs))
        return self.calculate_similarity(query, queryset)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.parent_category
        context["title"] = _("Category: %(name)s") % {"name": category.name}
        context["cat_selected"] = category.pk
        context["has_param"] = True
        context["param"] = category.slug
        return context


class ShowPostsByTag(DataMixin, SearchFieldMixin, ListView):
    template_name = "women/index.html"
    context_object_name = "posts"

    def get_queryset(self):
        tag_slug = self.kwargs["tag_slug"]
        query = self.request.GET.get("query")
        queryset = cache.get_or_set(f"cached_list_by_tag_{tag_slug}", Women.published.filter(tags__slug=tag_slug))
        return self.calculate_similarity(query, queryset)

    def get_context_data(self, *, object_list=None, **kwargs):
        tag_slug = self.kwargs["tag_slug"]
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(klass=TagPost, slug=tag_slug)
        context["title"] = _("Tag - %(tag)s") % {"tag": tag.tag}
        context["param"] = tag.slug
        return context


def tr_handler404(request, exception):
    error_message = str(exception) if exception else _("Unfortunately, this page was not found or has been moved")
    return render(request=request, template_name='errors/error_page.html', status=404, context={
        'title': _("Page not found: 404"),
        'error_message': error_message,
    })


def tr_handler500(request):
    return render(request=request, template_name='errors/error_page.html', status=500, context={
        'title': _("Server error: 500"),
        'error_message': _("Internal server error. Please return to the home page. We will send a report to the site administration."),
    })


def tr_handler403(request, exception):
    return render(request=request, template_name='errors/error_page.html', status=403, context={
        'title': _("Access error: 403"),
        'error_message': _("Access to this page is restricted"),
    })


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post_id = Women.objects.get(slug=self.kwargs.get("post_slug")).pk
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.body_ru = comment.body
        comment.body_en = comment.body
        comment.body_be = comment.body
        comment.save()
        translate_model_content.delay("Comment", "body", comment.pk)
        count_comments = Comment.objects.filter(post=comment.post_id, active=True, parent=None).count()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.pk,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'updated_text': _("%(text)s ago") % {"text": timesince(comment.updated)},
                'is_updated': comment.is_updated,
                'avatar': comment.author.thumbnail.url,
                'content': comment.body,
                'comment_url': reverse('edit_comment', args=(comment.post_id, comment.pk)),
                'get_absolute_url': comment.author.get_absolute_url(),
                'request_user': self.request.user.username,
                'post': comment.post_id,
                'parent_comment_author': comment.parent.author.username if comment.parent else None,
                'count_comments_text': ngettext(
                                "%(count)d comment",
                                  "%(count)d comments",
                                        count_comments
                                        ) % {'count': count_comments},
                'translations': {
                    'updated': _("Updated"),
                    'reply': _("Reply"),
                    'edit': _("Edit")
                },
                "lang": get_language()
            }, status=200)

        return redirect(comment.post.get_absolute_url())

    def handle_no_permission(self):
        return JsonResponse({'error': _("You must be logged in to add comments")}, status=400)


def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    post = get_object_or_404(Women, pk=post_id, is_published=Women.Status.PUBLISHED)
    if request.method == "GET":
        form = CommentForm(instance=comment)
    else:
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.body_ru = comment.body
            comment.body_en = comment.body
            comment.body_be = comment.body
            comment.is_updated = True
            comment.save()
            translate_model_content.delay("Comment", "body", comment.pk)
            messages.success(request, _("Comment successfully updated."))
            url = reverse("post", args=(post.slug,))
            return redirect(url)
    return render(request, "women/post/comment_edit.html",
                  {"form": form, "post": post})


class RatingCreateView(View):
    model = Rating

    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        value = int(request.POST.get('value'))
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        ip_address = ip
        user = request.user if request.user.is_authenticated else None

        rating, created = self.model.objects.get_or_create(
           post_id=post_id,
            ip_address=ip_address,
            defaults={'value': value, 'user': user},
        )

        if not created:
            if rating.value == value:
                rating.delete()
                return JsonResponse({'value': None, 'status': 'deleted', 'rating_sum': rating.post.get_sum_rating()})
            else:
                rating.value = value
                rating.user = user
                rating.save()
                return JsonResponse({'value': value, 'status': 'updated', 'rating_sum': rating.post.get_sum_rating()})
        return JsonResponse({'value': rating.value,'status': 'created', 'rating_sum': rating.post.get_sum_rating()})