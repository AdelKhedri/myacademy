from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import RecaptchaFrom, RegisterForm


class RegisterView(View):
    template_name = 'academy/register.html'

    def setup(self, request, *args, **kwargs):
        self.context = {
            'recaptcha': RecaptchaFrom(),
            'register_form': RegisterForm()
        }
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        recaptcha_form = RecaptchaFrom(request.POST)
        if recaptcha_form.is_valid():
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                res = register_form.send_otp_code_to_number()
                if not res:
                    self.context['msg'] = 'otp connection failed'
                return redirect('academi:confirm-account')
            else:
                self.context['register_form'] = register_form
                self.context['msg'] = 'register form error'
        else:
            self.context['msg'] = 'captcha error'
        return render(request, self.template_name, self.context)
