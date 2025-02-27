from academy.tests.tests_views import BaseTestCase
from django.urls import reverse
from user.models import Profile, User


class TestProfileView(BaseTestCase):
    def setUp(self):
        super().setUp()
        Profile.objects.create(user=self.user)

        self.profile_data = {
            'username': 'user',
            'email': 'user@gmail.com',
            'first_name': 'user',
            'last_name': 'rr',
            'about': 'bb'
        }
        User.objects.create(username='user2')
        self.url = reverse('user:profile')
        self.login()

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_redirect_anonymous_user(self):
        self.client.logout()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('academy:login') + '?next=%2Fprofile%2F', 302)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/profile.html')

    def test_update_username_success(self):
        self.login()
        res = self.client.post(self.url, data=self.profile_data, follow=True)
        self.assertTrue(res.wsgi_request.user.is_authenticated)
        self.assertContains(res, 'پروفایل با موفقیت آپدیت شد.')

    def test_update_username_failed_duplicated_username(self):
        data = self.profile_data
        data['username'] = 'user2'
        res = self.client.post(self.url, data=data)
        self.assertContains(res, ' نام کاربری تکراری است.')


class TestChangePasswordView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.change_password_data = {
            'new_password1': 'new_pass',
            'new_password2': 'new_pass',
            'last_password': 'password',
        }
        self.url = reverse('user:change-password')
        self.login()

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/change-password.html')

    def test_redirect_anonymous_user(self):
        self.client.logout()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('academy:login') + '?next=%2Fprofile%2Fchange-password%2F', 302)

    def test_change_password_success(self):
        res = self.client.post(self.url, data=self.change_password_data)
        self.assertRedirects(res, reverse('academy:login'), 302)

    def test_change_password_failed_invalid_last_password(self):
        data = self.change_password_data
        data['last_password'] = 'test'
        res = self.client.post(self.url, data=self.change_password_data)
        self.assertContains(res, 'پسورد قبلی اشتباه است.')

    def test_change_password_failed_not_matched_passwords(self):
        data = self.change_password_data
        data.update({
            'password1': 'test',
            'password2': 'tests',
            'last_password': 'asdasdas'
            })
        res = self.client.post(self.url, data=self.change_password_data)
        self.assertContains(res, 'پسورد باید ترکیبی از متن و عدد و بیشتر از ۷ کاراکتر باشد.')

