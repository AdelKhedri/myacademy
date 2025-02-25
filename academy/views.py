from random import randint
from django.shortcuts import render, redirect
from django.views.generic import View
from datetime import timedelta
from django.utils import timezone
from user.models import OTPCode, User
from .forms import RecaptchaFrom, RegisterForm, LoginForm
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.db.models import Q


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
                    return redirect(request.GET.get('next', 'academy:home'))
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
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        self.context = {}
        recaptcha_form = RecaptchaFrom(request.POST)
        if recaptcha_form:
            code = request.POST.get('code', None)
            if code and code.isnumeric():
                otp = OTPCode.objects.filter(code = code, phone_number = self.phone_number, time__lte = timedelta(minutes=4) + timezone.now())
                if otp.exists():
                    user = User.objects.get(phone_number = otp.first().phone_number)
                    user.is_active = True
                    user.save()
                    otp.delete()
                    request.session.pop('phone_number')
                    request.session.modified = True
                    if settings.LOGIN_AFTER_SIGNUP:
                        login(request, user)
                else:
                    self.context['msg'] = 'code failed'
            else:
                self.context['msg'] = 'code must be integer'
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
                        if timedelta(minutes=4) + last_otp.first().time < timezone.now() :
                            last_otp.delete()
                            send_code = True
                        else:
                            context['msg'] = 'please wait'
                    else:
                        send_code = True

                    if send_code:
                        code = randint(12121, 98989)
                        OTPCode.objects.create(code = code, phone_number = user.phone_number, code_type = 'forgot-password')
                        # try:
                        #     pass
                        #     #send code
                        # except:
                        #     context['msg'] = 'otp failed' # for error when try for send code to Phone number
                        # TODO: redirect to change password view
            else:
                context['msg'] = 'token failed'
        else:
            context['msg'] = 'ivalid captcha'
        context['recaptcha'] = recaptcha_form
        return render(request, self.template_name, context)
