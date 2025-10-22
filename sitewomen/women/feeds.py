from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import Women


class LatestPostFeed(Feed):
    title = _("My Django Blog – Latest Posts")
    description = _("New posts on my website.")

    def link(self):
        return reverse('latest_post_feed')

    def items(self):
        return Women.published.order_by('-time_update')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return reverse('post', args=[item.slug])