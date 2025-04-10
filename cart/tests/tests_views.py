import glob
import os
from django.urls import reverse
from cart.models import Cart, Order
from academy.models import Course
from academy.tests.tests_views import BaseTestCase
from django.core.files.uploadedfile import SimpleUploadedFile

class TestPaymentView(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.url = reverse('cart:payment')
        self.file_name = 'image_test_for_test_in_tests_.png'
        with open(f'user/tests/{self.file_name}', 'rb') as f:
            pic = SimpleUploadedFile(self.file_name, content=f.read(), content_type='image/png')

        Course.objects.create(
            name = 'test',
            teacher = self.user,
            description = 's',
            price = 33,
            thumbnail = pic,
            time = '01:00:00',
            difficulty_level = 'j',
        )

        self.logout_url = reverse('user:logout')
        self.login()

    def test_url(self):
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 302)

    def test_redirect_to_payment_address(self):
        res = self.client.post(self.url)
        self.assertRedirects(res, reverse('academy:home'), 302)

    def test_login_required(self):
        res = self.client.post(self.url)
        self.assertRedirects(res, reverse('academy:home'), 302)

    def test_get_request_not_accepted(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 405)

    def test_success_paid_and_redirect_to_bought_products(self):
        res = self.client.post(self.url)
        self.user.balance = 999999
        self.user.save()
        self.assertRedirects(res, reverse('academy:home'), 302)

    def tearDown(self):
        folder = f'media/courses/images'
        file_name = self.file_name
        file_name = file_name[:-4] + '*' + file_name[-4:]
        pattern = os.path.join(folder, file_name)

        for file in glob.glob(pattern):
            try:
                os.remove(file)
            except:
                pass
