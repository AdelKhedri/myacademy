from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import RecaptchaFrom, RegisterForm, LoginForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponse


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
                # return redirect('academi:confirm-account')
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
                # username = login_form.cleaned_data['username']
                # password = login_form.cleaned_data['password']
                user = authenticate(request, **login_form.cleaned_data)
                if user:
                    login(request, user)
                    return redirect(request.GET.get('next', 'academy:home'))
                self.context['msg'] = 'authentication failed'
            self.context['login_form'] = login_form
        else:
            self.context['msg'] = 'captcha error'
        return render(request, self.template_name, self.context)


def Home(request):
    return HttpResponse('ss')

