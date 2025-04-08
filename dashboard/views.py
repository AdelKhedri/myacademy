from django.views.generic import UpdateView, FormView, CreateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib import messages
from .forms import UserProfileForm, PasswordChangeForm
from academy.forms import CourseForm, SeasionFormSet
from user.models import Profile
from academy.models import Bookmark, Course, Seasion
from cart.models import Cart
from cart.utils import get_cart
from django.db.models import Count


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'dashboard/profile.html'
    model = Profile
    form_class = UserProfileForm
    success_url = reverse_lazy('user:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'profile'

        cart, total_price, cart_courses = get_cart(self.request.user)
        context['cart_courses'] = cart_courses
        context['total_price'] = total_price
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
    template_name = 'dashboard/change-password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('user:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'profile'

        cart, total_price, cart_courses = get_cart(self.request.user)
        context['cart_courses'] = cart_courses
        context['total_price'] = total_price
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect('user:login')


class CourseAddView(CreateView):
    model = Course
    form_class = CourseForm
    success_url = '/'
    template_name = 'dashboard/course.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('user:login') + '?next=' + reverse('dashboard:course-add'))
        elif not request.user.is_mentor:
            if not request.user.is_superuser:
                return redirect('dashboard:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'course-add'
        context['seasion_formset'] = SeasionFormSet(self.request.POST) if self.request.method == 'POST' else SeasionFormSet()
        
        cart, total_price, cart_courses = get_cart(self.request.user)
        context['cart_courses'] = cart_courses
        context['total_price'] = total_price
        return context

    def form_valid(self, form):
        seasion_formset = SeasionFormSet(self.request.POST)
        if seasion_formset.is_valid():
            self.object = form.save(teacher = self.request.user)

            seasion_instances = []
            for seasion_form in seasion_formset:
                if seasion_form.cleaned_data.get('title'):
                    seasion = seasion_form.save(commit=False)
                    seasion_instances.append(seasion)
            
            seasion_instances = Seasion.objects.bulk_create(seasion_instances)
            self.object.seasions.set(seasion_instances)

            return redirect(reverse('dashboard:course-update', args=[self.object.pk]))
        else:
            return self.form_invalid(form)


class CourseUpdateView(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'dashboard/course.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('user:login') + '?next=' + reverse('dashboard:course-update', args=[self.get_object().pk]))
        elif not request.user.is_mentor:
            if not request.user.is_superuser:
                return redirect('dashboard:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'course-update'

        cart, total_price, cart_courses = get_cart(self.request.user)
        context['cart_courses'] = cart_courses
        context['total_price'] = total_price
        return context

    def get_success_url(self):
        return reverse('dashboard:course-update', args=[self.get_object().pk])

    def form_valid(self, form):
        form.save(teacher = self.request.user)
        return self.render_to_response(self.get_context_data(form=form))

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Course.objects.none()
        return Course.objects.filter(teacher = self.request.user)


class CourseDeleteView(DeleteView):
    success_url = reverse_lazy('dashboard:my-courses')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('user:login') + '?next=' + reverse('dashboard:my-courses'))
        elif not request.user.is_mentor and not request.user.is_superuser:
            return redirect('dashboard:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Course.objects.filter(teacher = self.request.user)


class MyCourseView(ListView):
    template_name = 'dashboard/my-courses.html'
    paginate_by = 9

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('user:login') + '?next=' + reverse('dashboard:my-courses'))
        elif not request.user.is_mentor and not request.user.is_superuser:
            return redirect('dashboard:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Course.objects.filter(teacher = self.request.user, is_active = True).prefetch_related('seasions', 'related_course').annotate(lessons_count = Count('seasions__lessons')).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'my-courses'
        context['current_url'] = self.request.get_full_path()
        context['active_tab'] = 'published'
        context['active_courses'] = Course.objects.filter(teacher = self.request.user, is_active = True).count()
        context['inactive_courses'] = Course.objects.filter(teacher = self.request.user, is_active = False).count()
        context['all_bookmarks'] = [course.media_id for course in Bookmark.objects.filter(user = self.request.user)]

        cart, total_price, cart_courses = get_cart(self.request.user)
        context['cart_courses'] = cart_courses
        context['total_price'] = total_price
        return context


class MyCourseNotPublishedView(ListView):
    template_name = 'dashboard/my-courses.html'
    paginate_by = 9

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('user:login') + '?next=' + reverse('dashboard:my-courses-not-published'))
        elif not request.user.is_mentor and not request.user.is_superuser:
            return redirect('dashboard:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Course.objects.filter(teacher = self.request.user, is_active = False).prefetch_related('seasions', 'related_course').annotate(lessons_count = Count('seasions__lessons')).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'my-courses'
        context['current_url'] = self.request.get_full_path()
        context['active_tab'] = 'not-published'
        context['active_courses'] = Course.objects.filter(teacher = self.request.user, is_active = True).count()
        context['inactive_courses'] = Course.objects.filter(teacher = self.request.user, is_active = False).count()

        cart, total_price, cart_courses = get_cart(self.request.user)
        context['cart_courses'] = cart_courses
        context['total_price'] = total_price
        return context


class MyBookmarkListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/my-bookmark.html'
    paginate_by = 9

    def get_queryset(self):
        return Bookmark.objects.filter(user = self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'my_bookmarked_courses'

        cart, total_price, cart_courses = get_cart(self.request.user)
        context['cart_courses'] = cart_courses
        context['total_price'] = total_price
        return context
