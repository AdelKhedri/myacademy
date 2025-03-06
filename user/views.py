from django.shortcuts import redirect, render
from django.views.generic import UpdateView, FormView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserProfileForm, PasswordChangeForm
from .models import Profile
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from academy.models import Product, Seasion
from academy.forms import ProductForm, SeasionFormSet


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


class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'user/change-password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('academy:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'profile'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect('academy:login')


class ProductAddView(CreateView):
    model = Product
    form_class = ProductForm
    success_url = '/'
    template_name = 'user/add-product.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('academy:login') + '?next=' + reverse('user:product-add'))
        elif not request.user.is_teacher:
            if not request.user.is_superuser:
                return redirect('user:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'product-add'
        context['seasion_formset'] = SeasionFormSet(self.request.POST) if self.request.method == 'POST' else SeasionFormSet()
        return context

    def form_valid(self, form):
        seasion_formset = SeasionFormSet(self.request.POST)
        if seasion_formset.is_valid():
            self.object = form.save(user = self.request.user)

            seasion_instances = []
            for seasion_form in seasion_formset:
                if seasion_form.cleaned_data.get('title'):
                    seasion = seasion_form.save(commit=False)
                    seasion_instances.append(seasion)
            
            seasion_instances = Seasion.objects.bulk_create(seasion_instances)
            self.object.seasions.set(seasion_instances)

            messages.success(self.request, 'success')
            return self.render_to_response(self.get_context_data(form=form))
        else:
            return self.form_invalid(form)
