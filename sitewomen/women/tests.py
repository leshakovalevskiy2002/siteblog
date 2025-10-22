from http import HTTPStatus
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse, resolve
from django.utils import translation

from .forms import ContactForm
from .models import Women, Category
from . import views
from .views import HomePage
from sitewomen.settings import LANGUAGES


class WomenViewsTests(TestCase):
    fixtures = ['women_women.json', 'women_category.json', 'women_tagspost.json',
                "users_perms.json", "users_authors.json", "users_groups.json"]

    def setUp(self):
        self.home_path = reverse("home")
        self.home_response = self.client.get(self.home_path)
        self.all_posts = Women.published.select_related("cat", "author")

    def test_home_page_paginate_pages(self):
        num_pages = self.home_response.context_data["paginator"].num_pages
        page = 1
        paginate_by = HomePage.paginate_by

        while page <= num_pages:
            response = self.client.get(f"{self.home_path}?page={page}")
            self.assertQuerySetEqual(response.context_data["posts"],
                            self.all_posts[(page - 1) * paginate_by: page * paginate_by])
            page += 1

    def test_detail_post(self):
        for post in self.all_posts:
            path = reverse("post", args=(post.slug,))
            response = self.client.get(path)
            self.assertEqual(post.content, response.context_data["post"].content)


class WomenTemplateTests(TestCase):
    def setUp(self):
        url = reverse('home')
        self.response = self.client.get(url)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response, "women/index.html")

    def test_homepage_contains_correct_html(self):
        with translation.override("ru"):
            self.assertEqual(self.response.context.get("title"), "Главная")
        with translation.override("en"):
            self.assertEqual(self.response.context.get("title"), "Home page")
        with translation.override("be"):
            self.assertEqual(self.response.context.get("title"), "Галоўная")

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Incorrect HTML')


class WomenFormTests(TestCase):
    fixtures = ["users_perms.json", "some_users.json"]

    def setUp(self):
        self.client.login(username='test', password='jhonsina')
        path = reverse("contact")
        self.response = self.client.get(path)

    def test_contact_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, ContactForm)
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_bootstrap_class_used_for_default_styling(self):
        form = self.response.context.get('form')
        self.assertIn('class="form-control w-25"', form.as_p())

    def test_contact_form_validation_for_blank_items(self):
        contact_form = ContactForm(
            data={'name': '', 'email': '', 'comment': ''}
        )
        self.assertFalse(contact_form.is_valid())

    def test_contact_form_with_invalid_email(self):
        contact_form = ContactForm(
            data={'name': 'any_name', 'email': 'invalid', 'comment': '...'}
        )
        self.assertFalse(contact_form.is_valid())

    @patch('captcha.fields.CaptchaField.clean')
    def test_contact_form_with_correct_email(self, mock_clean):
        mock_clean.return_value = 'valid_captcha_value'
        contact_form = ContactForm(
            data={'name': 'any_name', 'email': 'test@list.ru', 'comment': '...',
                  "captcha": "valid_captcha_value"})
        self.assertTrue(contact_form.is_valid())


class WomenURLsTests(TestCase):
    fixtures = ["some_women_posts.json", "women_category.json"]

    def test_homepage_url_name(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_root_url_resolves_to_homepage_view(self):
        for code, _ in LANGUAGES:
            with translation.override(code):
                found = resolve(f'/{code}/')
                self.assertEqual(found.func.view_class, views.HomePage)

    def test_about_redirect(self):
        path = reverse("about")
        path_redirect = reverse("users:login")
        response = self.client.get(path)
        self.assertRedirects(response, f"{path_redirect}?next={path}",
                             HTTPStatus.FOUND, HTTPStatus.OK)

    def test_url_resolves_to_about_view(self):
        url = ["about", "о-сайте", "пра-сайт"]
        for i, (code, _) in enumerate(LANGUAGES):
            with translation.override(code):
                found = resolve(f'/{code}/{url[i]}/')
                self.assertEqual(found.func.view_class, views.About)

    def test_get_post_by_slug_url(self):
        path = reverse("post", args=("andzhelina-dzholi",))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        path = reverse("post", args=("unknow",))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_resolves_to_post_view(self):
        url = ["post", "пост", "паведамленне"]
        for i, (code, _) in enumerate(LANGUAGES):
            with translation.override(code):
                found = resolve(f'/{code}/{url[i]}/andzhelina-dzholi/')
                self.assertEqual(found.func.view_class, views.ShowPost)
                found = resolve(f'/{code}/{url[i]}/unknow/')
                self.assertEqual(found.func.view_class, views.ShowPost)


class WomenModelTests(TestCase):
    fixtures = ["women_cat.json"]

    def setUp(self):
        self.post = Women(
            title='Тестовая статья',
            content="Биография",
            is_published=1,
            cat_id=1
        )

    def test_create_post(self):
        self.assertIsInstance(self.post, Women)

    def test_str_representation(self):
        self.assertEqual(str(self.post), "Тестовая статья")

    def test_saving_and_retrieving_post(self):
        first_post = Women()
        first_post.title = 'Анджелина Джоли'
        first_post.content = 'Биография Анджелины Джоли'
        first_post.is_published = 1
        first_post.cat_id = 2
        first_post.save()

        second_post = Women()
        second_post.title = 'Марго Робби'
        second_post.content = 'Биография Марго Робби'
        second_post.is_published = 0
        second_post.cat_id = 1
        second_post.save()

        saved_posts = Women.objects.all()
        saved_published_posts = Women.published.all()
        self.assertEqual(saved_published_posts.count(), 1)

        first_post_by_ordering = saved_posts[0]
        second_post_by_ordering = saved_posts[1]
        self.assertEqual(first_post_by_ordering.title, 'Марго Робби')
        self.assertEqual(second_post_by_ordering.content, 'Биография Анджелины Джоли')
        self.assertIsInstance(second_post_by_ordering.cat, Category)
        self.assertEqual(second_post_by_ordering.is_published, 1)
        self.assertEqual(first_post_by_ordering.photo, "photos/placeholder300.jpg")


class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category(name='Актрисы')

    def test_create_post(self):
        self.assertIsInstance(self.category, Category)

    def test_str_representation(self):
        self.assertEqual(str(self.category), 'Актрисы')

    def test_saving_and_retrieving_post(self):
        parent_cat = Category()
        parent_cat.name = 'Актрисы'
        parent_cat.save()

        cat = Category()
        cat.title = 'Известные'
        cat.parent = parent_cat
        cat.save()

        saved_cats = Category.objects.all()
        self.assertEqual(saved_cats.count(), 2)

        first_cat = saved_cats[0]
        second_cat = saved_cats[1]
        self.assertEqual(first_cat.name, 'Актрисы')
        self.assertIsInstance(second_cat.parent, Category)