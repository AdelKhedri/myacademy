from academy.tests.tests_views import BaseTestCase
from django.urls import reverse
from user.models import OTPCode
from unittest.mock import patch
from django_recaptcha.client import RecaptchaResponse
from freezegun import freeze_time
from datetime import datetime, timedelta
from django.utils import timezone


class TestLoginView(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_url_exist(self):
        res = self.client.get(self.login_url)
        self.assertEqual(res.status_code, 200)

    def test_template(self):
        res = self.client.get(self.login_url)
        self.assertTemplateUsed(res, 'user/login.html')

    @patch('django_recaptcha.fields.client.submit')
    def test_fail_login_user_not_exist(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        self.user_data['username'] = 'test'
        res = self.client.post(self.login_url, data=self.user_data)
        self.assertEqual(res.context['msg'], 'authentication failed')
        self.assertContains(res, 'کاربری با این مشخصات یافت نشد.')

    def test_failed_login_recaptcha(self):
        del self.user_data['g-recaptcha-response']
        res = self.client.post(self.login_url, data=self.user_data)
        self.assertEqual(res.context['msg'], 'captcha error')
        self.assertContains(res, 'لطفا کپچا رو تایید کنید.')

    @patch('django_recaptcha.fields.client.submit')
    def test_login_success(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        res = self.client.post(self.login_url, data=self.user_data)
        self.assertEqual(res.wsgi_request.user.username, 'user1')


class TestRegisterView(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.url = reverse('user:register')
        self.register_data = {
            'username': 'user2',
            'email': 'user2@gmail.com',
            'phone_number': '09123456788',
            'password1': 'test1234',
            'password2': 'test1234',
            'g-recaptcha-response': 'mocked-captcha-response',
            'accept_rules': True
        }

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/register.html')


    @patch("django_recaptcha.fields.client.submit")
    def test_register_success(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)

        res = self.client.post(self.url, self.register_data)
        res2 = self.client.get(self.url)
        self.assertEqual(res.wsgi_request.session.get('phone_number', None), self.register_data['phone_number'])
        # self.assertEqual(res.status_code, 302)

    @patch("django_recaptcha.fields.client.submit")
    def test_register_unique_username(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)

        self.register_data['username'] = 'user1'
        res = self.client.post(self.url, self.register_data)
        self.assertContains(res, 'کاربر با این نام کاربری از قبل موجود است.')

    @patch("django_recaptcha.fields.client.submit")
    def test_register_unique_email(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)

        self.register_data['email'] = 'user1@gmail.com'
        res = self.client.post(self.url, self.register_data)
        self.assertContains(res, 'کاربر با این ایمیل از قبل موجود است.')

    @patch("django_recaptcha.fields.client.submit")
    def test_register_unique_phone_number(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)

        self.register_data['phone_number'] = '09123456789'
        res = self.client.post(self.url, self.register_data)
        self.assertContains(res, 'کاربر با این شماره تلفن از قبل موجود است.')

    def test_captcha_failed(self):
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'لطفا کپچا رو تایید کنید.')


class TestActiveRegisterdAccountView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.register_data = {
            'username': 'user2',
            'password1': 'password',
            'password2': 'password',
            'email': 'user2@gmail.com',
            'phone_number': '09123789456',
            'accept_rules': True,
            'g-recaptcha-response': 'RESPONSE',
        }
        self.register_url = reverse('user:register')
        self.url = reverse('user:active-account')

    @patch('django_recaptcha.fields.client.submit')
    def test_url(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid = True)

        res = self.client.post(self.register_url, data=self.register_data)
        # print(res.content.decode('utf-8'))
        self.assertEqual(res.status_code, 302)

    @patch('django_recaptcha.fields.client.submit')
    def test_template_used(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid = True)

        res = self.client.post(self.register_url, data=self.register_data)
        self.assertEqual(res.status_code, 302)
        
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/activate.html')

    def test_redirect_registered_user(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)

    def test_redirect_none_phone_number_in_session(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('user:register'))

    @patch('django_recaptcha.fields.client.submit')
    def test_active_account(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid = True)

        res = self.client.post(self.register_url, self.register_data)
        self.assertEqual(res.wsgi_request.session.get('phone_number', None), self.register_data['phone_number'])
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('user:active-account'))

        code = OTPCode.objects.get(id = 1)
        res = self.client.post(self.url, data={'g-recaptcha-response': 'RESPONSE', 'code': code.code})
        self.assertTrue(res.wsgi_request.user.is_authenticated)


class TestForgotPasswordView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('user:forgot-password')

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/forgot-password.html')

    @patch('django_recaptcha.fields.client.submit')
    def test_success_send_code_with_phone_number(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'token': '09123456789'
        }
        
        res = self.client.post(self.url, data=data)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('user:confirm-forgot-password'))

    @patch('django_recaptcha.fields.client.submit')
    def test_success_send_link_with_email(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'token': 'user1@gmail.com'
        }

        res = self.client.post(self.url, data=data)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('user:confirm-forgot-password'))

    @patch('django_recaptcha.fields.client.submit')
    def test_success_send_code_with_username(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'token': 'user1'
        }
        
        res = self.client.post(self.url, data=data)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('user:confirm-forgot-password'))

    @patch('django_recaptcha.fields.client.submit')
    def test_failed_send_code_number_not_found(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'token': '65231'
        }

        res = self.client.post(self.url, data=data)
        self.assertContains(res, 'نام کاربری/ایمیل/شماره تلفن اشتباه است.')

    @patch('django_recaptcha.fields.client.submit')
    def test_failed_send_link_last_sended(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'token': '09123456789'
        }

        res = self.client.post(self.url, data=data)
        res = self.client.post(self.url, data=data)
        self.assertContains(res, 'ارسال کد در فاصله های 4 دقیقه پس از اخرین ارسال کد مجاز است.')


    @freeze_time(datetime.now())
    @patch('django_recaptcha.fields.client.submit')
    def test_failed_send_link_last_sended(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        start_time = datetime.now()
        data = {
            'g-recaptcha-response': 'RESPONSE',
            'number': '09123456789'
        }

        res = self.client.post(self.url, data=data)

        # freeze time
        with freeze_time(start_time + timedelta(minutes=5, seconds=2)):
            res = self.client.post(self.url, data=data)
            self.assertEqual(res.status_code, 200)

    def test_redirect_authorized_user(self):
        self.login()
        res = self.client.post(self.url, data={})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('academy:home'), 302, 200)


class ConfirmTestForgotPasswordView(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.otp_code = OTPCode.objects.create(
            phone_number = self.user.phone_number,
            expire_time=timezone.now() + timedelta(minutes=4),
            code = 22266,
            code_type = 'forgot-password')
        self.data = {
            'g-recaptcha-response': 'RESPONSE',
            'code': self.otp_code.code,
            'password1': 'new_pass',
            'password2': 'new_pass',
        }
        self.url = reverse('user:confirm-forgot-password')
        session = self.client.session
        session['phone_number'] = self.user.phone_number
        session.save()

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/confirm-forgot-password.html')

    def test_redirect_authoraized_user(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('academy:home'))

    def test_redirect_user_without_phone_number_in_session(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('academy:home'))

    @patch('django_recaptcha.fields.client.submit')
    def test_change_password_success(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)

        res = self.client.post(self.url, self.data)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, res.wsgi_request.GET.get('next', reverse('user:login')))
        self.assertNotIn(self.user.phone_number, res.wsgi_request.session)

    @patch('django_recaptcha.fields.client.submit')
    def test_change_password_failed_invalid_code(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    @patch('django_recaptcha.fields.client.submit')
    def test_change_password_failed_invalid_recaptcha(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'کپچا اشتباه حل شده.')

    @freeze_time(datetime.now())
    @patch('django_recaptcha.fields.client.submit')
    def test_change_password_failed_expire_code(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)

        self.data['code'] = 22
        start_time = datetime.now()
        with freeze_time(start_time, timedelta(minutes=4, seconds=1)):
            res = self.client.post(self.url, self.data)
            self.assertContains(res, 'کد اشتباه است یا منقضی شده.')


class TestLogoutView(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.url = reverse('user:logout')
        self.login()

    def test_url(self):
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse('academy:home'), 302)

    def test_redirect_anonymous_user(self):
        self.client.logout()
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse('user:login'), 302)

    def test_logout_user(self):
        res = self.client.get(self.url)
        self.assertTrue(res.wsgi_request.user.is_anonymous)
        self.assertRedirects(res, reverse('academy:home'))
