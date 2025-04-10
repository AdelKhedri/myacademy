import glob
import os
from unittest.mock import patch
from django_recaptcha.client import RecaptchaResponse
from django.test import TestCase
from academy.models import Category, Course
from user.models import Profile, User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='user1', email='user1@gmail.com', phone_number='09123456789')
        self.user.set_password('password')
        self.user.is_active = True
        self.user.is_teacher = True
        self.user.is_superuser = True
        self.user.save()
        Profile.objects.create(user = self.user)

        self.user_data = {
            'username': 'user1',
            'password': 'password',
            'g-recaptcha-response': 'RESPONSE'
        }
        self.login_url = reverse('user:login')

    @patch('django_recaptcha.fields.client.submit')
    def login(self, mocked_value):
        mocked_value.return_value = RecaptchaResponse(is_valid=True)
        self.client.post(self.login_url, data=self.user_data)


class TestCourseFilterView(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.url = reverse('academy:courseslist')
        self.login()

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
            res = self.client.get(self.url)
            self.assertTemplateUsed(res, 'academy/course.html')


class TestCourseCategoryView(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.file_name = 'image_test_for_test_in_tests_.png'
        with open(f'user/tests/{self.file_name}', 'rb') as f:
            pic = f.read()
        pic = SimpleUploadedFile(name=self.file_name, content=pic, content_type='image/png')

        course = Course.objects.create(
            name = 'test',
            teacher = self.user,
            thumbnail = pic,
            is_active = True,
            time = '02:02:02'
        )
        category = Category.objects.create(title = 'test1', slug = 'title')
        course.category.add(category)
        self.url = reverse('academy:category', args=[category.slug])

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'academy/course.html')

    def test_not_found_category_with_code_404(self):
        res = self.client.get(reverse('academy:category', kwargs={'category_slug': 'sss'}))
        self.assertEqual(res.status_code, 404)

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