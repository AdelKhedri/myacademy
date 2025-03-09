from django.shortcuts import redirect, render
from django.views.generic import UpdateView, FormView, CreateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.db.models import Count
from .forms import UserProfileForm, PasswordChangeForm
from .models import Profile
from academy.models import Course, Seasion
from academy.forms import CourseForm, SeasionFormSet


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


class CourseAddView(CreateView):
    model = Course
    form_class = CourseForm
    success_url = '/'
    template_name = 'user/course.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('academy:login') + '?next=' + reverse('user:course-add'))
        elif not request.user.is_teacher:
            if not request.user.is_superuser:
                return redirect('user:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'course-add'
        context['seasion_formset'] = SeasionFormSet(self.request.POST) if self.request.method == 'POST' else SeasionFormSet()
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

            return redirect(reverse('user:course-update', args=[self.object.pk]))
        else:
            return self.form_invalid(form)


class CourseUpdateView(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'user/course.html'

    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('academy:login') + '?next=' + reverse('user:course-update', args=[self.get_object().pk]))
        elif not request.user.is_teacher:
            if not request.user.is_superuser:
                return redirect('user:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'course-update'
        return context

    def get_success_url(self):
        return reverse('user:course-update', args=[self.get_object().pk])

    def form_valid(self, form):
        form.save(teacher = self.request.user)
        return self.render_to_response(self.get_context_data(form=form))

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Course.objects.none()
        return Course.objects.filter(teacher = self.request.user)


class MyCourseView(ListView):
    template_name = 'user/my-courses.html'
    paginate_by = 9

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('academy:login') + '?next=' + reverse('user:my-courses'))
        elif not request.user.is_teacher and not request.user.is_superuser:
            return redirect('user:profile')
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
        return context


# Yes i know but,
# i cannot have 2 pagination
# i cannot modified inactive pagination and active pagination
class MyCourseNotPublishedView(ListView):
    template_name = 'user/my-courses.html'
    paginate_by = 9

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('academy:login') + '?next=' + reverse('user:my-courses-not-published'))
        elif not request.user.is_teacher and not request.user.is_superuser:
            return redirect('user:profile')
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
        return context


class CourseDeleteView(DeleteView):
    success_url = reverse_lazy('user:my-courses')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('academy:login') + '?next=' + reverse('user:my-courses'))
        elif not request.user.is_teacher and not request.user.is_superuser:
            return redirect('user:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Course.objects.filter(teacher = self.request.user)


class MyBookmarkListView(LoginRequiredMixin, ListView):
    template_name = 'user/my-bookmark.html'
    paginate_by = 9

    def get_queryset(self):
        courses_list = [course.pk for course in self.request.user.profile.bookmarks.all()]
        return Course.objects.filter(is_active = True, pk__in = courses_list).select_related('teacher').prefetch_related('related_course', 'seasions', 'category').annotate(lessons_count = Count('seasions__lessons')).order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_url'] = self.request.get_full_path()
        context['current_page'] = 'my_bookmarked_courses'
        return context
