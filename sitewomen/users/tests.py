from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import translation


class RegisterUserTestCase(TestCase):
    fixtures = ["users_perms.json"]

    def setUp(self):
        self.data = {
            'username': 'user_1',
            'email': 'user1@sitewomen.ru',
            'first_name': 'Sergey',
            'last_name': 'Balakirev',
            'password1': '12345678Aa',
            'password2': '12345678Aa',
        }

    def test_form_registration_get(self):
        path = reverse("users:registration")
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/registration.html")

    def test_form_registration_success(self):
        user_model = get_user_model()
        path = reverse('users:registration')
        response = self.client.post(path, self.data)
        self.assertRedirects(response, reverse('users:confirm_email'), HTTPStatus.FOUND, HTTPStatus.OK)
        user = user_model.objects.filter(username=self.data['username'])
        self.assertTrue(user.exists())
        self.assertFalse(user[0].email_verified)

    def test_user_registration_password_error(self):
        self.data["password2"] = '12345678A'

        with translation.override('en'):
            path = reverse("users:registration")
            response = self.client.post(path, self.data)
            form = response.context['form']
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn("The two password fields didn’t match.", form.errors["password2"])

        with translation.override('ru'):
            path = reverse("users:registration")
            response = self.client.post(path, self.data)
            form = response.context['form']
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn("Введенные пароли не совпадают.", form.errors["password2"])

        with translation.override('be'):
            path = reverse("users:registration")
            response = self.client.post(path, self.data)
            form = response.context['form']
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn("Не супадаюць паролі ў двух палях.", form.errors["password2"])

    def test_user_registration_username_error(self):
        user_model = get_user_model()
        user_model.objects.create(username=self.data["username"])

        with translation.override('ru'):
            path = reverse("users:registration")
            response = self.client.post(path, self.data)
            form = response.context['form']
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn("Пользователь с таким именем уже существует.", form.errors["username"])

        with translation.override('en'):
            path = reverse("users:registration")
            response = self.client.post(path, self.data)
            form = response.context['form']
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn("A user with that username already exists.", form.errors["username"])

        with translation.override('be'):
            path = reverse("users:registration")
            response = self.client.post(path, self.data)
            form = response.context['form']
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn("Карыстальнік з такім іменем ужо існуе.", form.errors["username"])