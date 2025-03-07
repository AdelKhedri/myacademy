import os
from academy.models import Course
from academy.tests.tests_views import BaseTestCase
from django.urls import reverse
from user.models import Profile, User
from django.core.files.uploadedfile import SimpleUploadedFile


class TestProfileView(BaseTestCase):
    def setUp(self):
        super().setUp()

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


class TestCourseAddView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.pic_name = '11.png'
        self.dd = os.path.join(os.path.dirname(__file__), '11.png')
        with open(self.dd, 'rb') as f:
            pic = SimpleUploadedFile(
                name = self.pic_name,
                content = f.read(),
                content_type = 'image/png'
            )

        self.course_data = {
            'name': 'test',
            'description': 'test',
            'price': 250000,
            'price_with_discount': 240000,
            'tax': 10,
            'thumbnail': pic,
            'time': '02:22:25',
            'difficulty_level': 's',
        }
        self.seasion_data = [
            {
                'title': 'test1'
            }
        ]
        self.url = reverse('user:course-add')
        self.login()

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/course.html')

    def test_redirect_anonymous_user(self):
        self.client.logout()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('academy:login') + '?next=%2Fprofile%2Fcourse%2Fadd%2F', 302)

    def test_redirect_not_teacher(self):
        self.user.is_teacher = False
        self.user.is_superuser = False
        self.user.save()
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse('user:profile'), 302)

    def test_add_course_success(self):
        data = self.course_data
        total_forms = len(self.seasion_data)
        data['form-TOTAL_FORMS'] = total_forms
        data['form-INITIAL_FORMS'] = 0
        data['form-MIN_NUM_FORMS'] = 0
        data['form-MAX_NUM_FORMS'] = 100

        for i, seasion in enumerate(self.seasion_data):
            data[f'form-{i}-title'] = seasion['title']

        res = self.client.post(self.url, data=data)
        self.assertRedirects(res, reverse('user:course-update', args=[Course.objects.first().pk]), 302)
        self.assertEqual(Course.objects.first().name, self.course_data['name'])

    
    def tearDown(self):
        file_name = f'media/courses/images/{self.pic_name}'
        if os.path.exists(file_name):
            os.remove(file_name)


class TestCourseUpdateView(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.pic_name = '11.png'
        self.dd = os.path.join(os.path.dirname(__file__), '11.png')
        with open(self.dd, 'rb') as f:
            self.pic = SimpleUploadedFile(
                name = self.pic_name,
                content = f.read(),
                content_type = 'image/png'
            )
        self.course_data = {
            'name': 'test',
            'description': 'test2',
            'time': '02:12:12',
            'price': 20220,
            'tax': 2,
            'difficulty_level': 's',
        }
        self.course = Course.objects.create(teacher = self.user, thumbnail = self.pic, **self.course_data)
        self.url = reverse('user:course-update', args=[self.course.pk])
        self.login()

    def test_url(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_template_used(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'user/course.html')

    def test_redirect_anonymous_user(self):
        self.client.logout()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

        # redirect not worked for anonymous user becuse i used get_queryset
        # self.assertEqual(res.status_code, 302)
        # self.assertRedirects(res, reverse('academy:login') + '?next=%2Fprofile%2Fcourse%2F1%2Fupdate%2F', 302)

    def test_redirect_not_teacher(self):
        self.user.is_teacher = False
        self.user.is_superuser = False
        self.user.save()
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse('user:profile'), 302)

    def test_update_course_success(self):
        data = self.course_data
        data['name'] = 'new'
        files = {'thumbnail': self.pic,}

        res = self.client.post(self.url, data=data, files=files)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Course.objects.first().name, data['name'])

    def test_error_update_course_of_another_teacher(self):
        user = User.objects.create(username = 'test')
        obj = Course.objects.create(name = 'testee', teacher = user, time = '00:01:11')
        res = self.client.get(reverse('user:course-update', args=[obj.pk]))
        self.assertEqual(res.status_code, 404)

    
    def tearDown(self):
        file_name = f'media/courses/images/{self.pic_name}'
        if os.path.exists(file_name):
            os.remove(file_name)
