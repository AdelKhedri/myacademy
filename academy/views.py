from random import randint
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View
from datetime import timedelta
from django.utils import timezone
from .models import Category, Course
from user.models import OTPCode, User
from .forms import RecaptchaFrom, RegisterForm, LoginForm, ChangePasswordForgotPasswordFrom
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator


def paginate(queryset, per_page, request):
    page = str(request.GET.get('page', 1))
    if not page.isnumeric():
        page = 1
    paginator = Paginator(queryset, per_page)
    return paginator.page(page)


class RegisterView(View):
    template_name = 'academy/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('academy:home')
        self.context = {
            'recaptcha': RecaptchaFrom(),
            'register_form': RegisterForm()
        }
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        recaptcha_form = RecaptchaFrom(request.POST)
        if recaptcha_form.is_valid():
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                request.session['phone_number'] = register_form.cleaned_data['phone_number']
                request.session.modified = True
                res = register_form.send_otp_code_to_number()
                if not res:
                    self.context['msg'] = 'otp connection failed'
                return redirect('academy:active-account')
            else:
                self.context['register_form'] = register_form
                self.context['msg'] = 'register form error'
        else:
            self.context['msg'] = 'captcha error'
        return render(request, self.template_name, self.context)


class LoginView(View):
    template_name = 'academy/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('academy:home')

        self.context = {
            'login_form': LoginForm(),
            'recaptcha': RecaptchaFrom(),
        }
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        recaptcha_form = RecaptchaFrom(request.POST)
        if recaptcha_form.is_valid():
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = authenticate(request, **login_form.cleaned_data)
                if user:
                    login(request, user)
                    # TODO: Add login redirect url
                    return redirect(request.GET.get('next', 'user:profile'))
                self.context['msg'] = 'authentication failed'
            self.context['login_form'] = login_form
        else:
            self.context['msg'] = 'captcha error'
        return render(request, self.template_name, self.context)


def Home(request):
    return HttpResponse('ss')


class ActivateRegisterdAccountView(View):
    template_name = 'academy/activate.html'

    def dispatch(self, request, *args, **kwargs):
        self.phone_number = request.session.get('phone_number', None)
        if request.user.is_authenticated:
            return redirect('academy:home')
        elif self.phone_number is None:
            return redirect('academy:register')

        self.context = {
            'msg': 'code sended',
            'recaptcha': RecaptchaFrom()
            }
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.context = {
            'recaptcha': RecaptchaFrom()
        }
        recaptcha_form = RecaptchaFrom(request.POST)
        if recaptcha_form.is_valid():
            code = request.POST.get('code', None)
            if code and code.isnumeric():
                otp = OTPCode.objects.filter(code = code, phone_number = self.phone_number, expire_time__gte = timezone.now())
                if otp.exists():
                    user = User.objects.get(phone_number = otp.first().phone_number)
                    user.is_active = True
                    user.save()
                    otp.delete()
                    request.session.pop('phone_number')
                    request.session.modified = True
                    if settings.LOGIN_AFTER_SIGNUP:
                        login(request, user)
                    if settings.LOGIN_AFTER_SIGNUP_URL:
                        return redirect(settings.LOGIN_AFTER_SIGNUP_URL)
                    else:
                        return redirect('academy:home')
                else:
                    self.context['msg'] = 'code failed'
            else:
                self.context['msg'] = 'code must be integer'
        else:
            self.context['msg'] = 'invalid captcha'
        return render(request, self.template_name, self.context)


class ForgotPasswordView(View):
    template_name = 'academy/forgot-password.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('academy:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'recaptcha': RecaptchaFrom()})

    def post(self, request, *args, **kwargs):
        recaptcha_form = RecaptchaFrom(request.POST)
        context = {}

        if recaptcha_form.is_valid():
            token = request.POST.get('token', None)
            if token:
                try:
                    user = User.objects.get(Q(username = token) | Q(email = token) | Q(phone_number = token))

                except:
                    context['msg'] =  'user not found'
                else:
                    last_otp = OTPCode.objects.filter(phone_number = user.phone_number, code_type='forgot-password')
                    send_code = False
                    if last_otp.exists():
                        if last_otp.first().expire_time < timezone.now() :
                            last_otp.delete()
                            send_code = True
                        else:
                            context['msg'] = 'please wait'
                    else:
                        send_code = True

                    if send_code:
                        code = randint(12121, 98989)
                        OTPCode.objects.create(code = code, expire_time = timedelta(minutes=5) + timezone.now(), phone_number = user.phone_number, code_type = 'forgot-password')
                        
                        request.session['phone_number'] = user.phone_number
                        request.session.modified = True
                        # try:
                        #     pass
                        #     #send code
                        # except:
                        #     context['msg'] = 'otp failed' # for error when try for send code to Phone number
                        return redirect('academy:confirm-forgot-password')
            else:
                context['msg'] = 'token failed'
        else:
            context['msg'] = 'ivalid captcha'
        context['recaptcha'] = recaptcha_form
        return render(request, self.template_name, context)


class ConfirmForgotPasswordView(View):
    template_name = 'academy/confirm-forgot-password.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('academy:home')
        self.phone_number = request.session.get('phone_number', None)
        if self.phone_number is None:
            return redirect('academy:home')

        self.context = {
            'recaptcha': RecaptchaFrom(),
            'change_password_form': ChangePasswordForgotPasswordFrom()
        }
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        recaptcha_form = RecaptchaFrom(request.POST)
        if recaptcha_form.is_valid():
            change_password_form = ChangePasswordForgotPasswordFrom(request.POST)
            if change_password_form.is_valid():
                code = change_password_form.cleaned_data['code']
                otp = OTPCode.objects.filter(Q(code_type = 'forgot-password'), phone_number = self.phone_number)
                otp_with_code  = otp.filter(code = code, expire_time__gte = timezone.now())
                if otp_with_code.exists():
                    user = User.objects.get(phone_number = otp_with_code.first().phone_number)
                    user.set_password(change_password_form.cleaned_data['password1'])
                    user.save()
                    otp.delete()
                    request.session.pop('phone_number')
                    request.session.modified = True
                    # TODO: Redirect to user panel
                    # TODO: if on settings set can auto login after change password and redirect to user panel
                    return redirect(request.GET.get('next', 'academy:login'))
                else:
                    self.context['msg'] = 'invalid code'
            self.context['change_password_form'] = change_password_form
        else:
            self.context['msg'] = 'invalid recaptcha'
        return render(request, self.template_name, self.context)


class CourseFilterView(View):
    template_name = 'academy/course.html'

    def get(self, request, *args, **kwargs):
        courses = Course.objects.filter(is_active = True).select_related('teacher').prefetch_related('category', 'seasions').annotate(lessons_count = Count('seasions__lessons')).order_by('updated_at')
        course_name = request.GET.get('name', None)
        if course_name:
            courses = courses.filter(name__contains = course_name)

        context = {
            'courses': paginate(courses, 9, request),
            'page_name': 'تمام دوره ها | آکادمی من'
            }
        return render(request, self.template_name, context)


class CourseCategoryView(View):
    template_name = 'academy/course.html'

    def get(self, request, category_slug, *args, **kwargs):
        category = get_object_or_404(Category, slug = category_slug)
        courses = Course.objects.filter(is_active = True, category__slug = category_slug).select_related('teacher').prefetch_related('category', 'seasions').annotate(lessons_count = Count('seasions__lessons')).order_by('updated_at')
        course_name = request.GET.get('name', None)
        if course_name:
            courses = courses.filter(name__contains = course_name)

        context = {
            'courses': paginate(courses, 9, request),
            'page_name': f'دوره های {category.title} | آکادمی من'
            }
        return render(request, self.template_name, context)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('academy:login')
        logout(request)
        return redirect('academy:home')
