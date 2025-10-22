from django.urls import path, register_converter
from django.utils.translation import gettext_lazy as _

from . import views, converters


register_converter(converters.YearConverter, "year4")

urlpatterns = [
    path('', views.HomePage.as_view(), name="home"),
    path(_('about/'), views.About.as_view(), name="about"),
    path(_('addpage/'), views.AddPage.as_view(), name='add_page'),
    path(_('contact/'), views.Contact.as_view(), name='contact'),
    path(_('post/<slug:post_slug>/'), views.ShowPost.as_view(), name="post"),
    path(_('category/<slug:cat_slug>/'), views.ShowCategory.as_view(), name='category'),
    path(_("tag/<slug:tag_slug>/"), views.ShowPostsByTag.as_view(), name="tag"),
    path(_("edit_post/<slug:slug>/"), views.UpdatePage.as_view(), name="edit_post"),
    path(_("delete_post/<slug:slug>/"), views.DeletePage.as_view(), name="delete_post"),
    path('post/<slug:post_slug>/comments/create/', views.CommentCreateView.as_view(), name='comment_create_view'),
    path('edit_comment/<int:post_id>/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('rating/', views.RatingCreateView.as_view(), name='rating'),
]
