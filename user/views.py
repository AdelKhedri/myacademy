from django.shortcuts import render
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserProfileForm
from .models import Profile
from django.urls import reverse_lazy
from django.contrib import messages


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'user/profile.html'
    model = Profile
    form_class = UserProfileForm
    success_url = reverse_lazy('user:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'profile'
        return context

    def get_object(self):
        return self.request.user.profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'پروفایل با موفقیت آپدیت شد.')
        return self.render_to_response(self.get_context_data(form=form))
