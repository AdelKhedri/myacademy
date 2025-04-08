from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic import View
from cart.models import Cart
from cart.utils import get_cart
from .models import Bookmark, Category, Course, MainPageCategoryAdd, MainPageCourseAdd, Team
from .forms import CommentForm
from django.db.models import Count
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from academy.models import Comment


def paginate(queryset, per_page, request):
    page = str(request.GET.get('page', 1))
    if not page.isnumeric():
        page = 1
    paginator = Paginator(queryset, per_page)
    return paginator.page(page)


class Home(View):
    template_name = 'academy/home.html'

    def get(self, request, *args, **kwargs):
        context = {
            'mainpage_categorys': MainPageCategoryAdd.objects.all()[:4],
            'mainpage_tabs_courses': MainPageCourseAdd.objects.all()[:4],
            'team': Team.objects.all(),
        }

        if request.user.is_authenticated:
            cart, total_price, cart_courses = get_cart(request.user)
            all_bookmarks = [course.media_id for course in Bookmark.objects.filter(user = request.user)]

            context.update({
                'total_price': total_price,
                'cart_courses': cart_courses,
                'all_bookmarks': all_bookmarks,
            })
        return render(request, self.template_name, context)


class CourseFilterView(View):
    template_name = 'academy/course.html'

    def get(self, request, *args, **kwargs):

        courses = Course.objects.filter(is_active = True).select_related('teacher').prefetch_related('category', 'seasions').annotate(lessons_count = Count('seasions__lessons')).order_by('updated_at')
        course_name = request.GET.get('name', None)
        if course_name:
            courses = courses.filter(name__contains = course_name)

        context = {
            'courses': paginate(courses, 9, request),
            'current_url': request.get_full_path(),
            'page_name': 'تمام دوره ها | آکادمی من',
            }

        if request.user.is_authenticated:
            cart, total_price, cart_courses = get_cart(request.user)
            all_bookmarks = [course.media_id for course in Bookmark.objects.filter(user = request.user)]

        context.update({
            'total_price': total_price,
            'cart_courses': cart_courses,
            'all_bookmarks': all_bookmarks,
        })
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
            'page_name': f'دوره های {category.title} | آکادمی من',
            }

        if request.user.is_authenticated:
            cart, total_price, cart_courses = get_cart(request.user)
            all_bookmarks = [course.media_id for course in Bookmark.objects.filter(user = request.user)]

            context.update({
                'total_price': total_price,
                'cart_courses': cart_courses,
                'all_bookmarks': all_bookmarks,
            })
        return render(request, self.template_name, context)


class BookmarkView(LoginRequiredMixin, View):
    def post(self, request, content_type, course_id, *args, **kwargs):
        content_types = {
            'course': Course,
        }
        if content_type not in content_types.keys():
            raise Http404()
        course = get_object_or_404(content_types[content_type], id=course_id)

        bookmark, created = Bookmark.objects.get_or_create(user = request.user, content_type = content_type, media_id = course_id)
        if not created: bookmark.delete()

        return redirect(request.GET.get('next', reverse('academy:courseslist')))


class CourseDetailsView(View):
    template_name = 'academy/course-details.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(
            Course.objects.prefetch_related('category', 'seasions', 'seasions__lessons').select_related('teacher').annotate(lessons_count = Count('seasions__lessons')),
            is_active = True,
            id = kwargs['course_id']
            )

        self.context = {
            'course': self.course,
            'comments': Comment.objects.filter(active = True, media_type = 'course', parent__isnull = True, media_id = self.course.pk),
            'form': CommentForm(),
        }

        if request.user.is_authenticated:
            cart, total_price, cart_courses = get_cart(request.user)
            all_bookmarks = [course.media_id for course in Bookmark.objects.filter(user = request.user)]
            product_in_cart = cart_courses.filter(media_id = self.course.id)

            self.context.update({
                'product_in_cart': product_in_cart,
                'total_price': total_price,
                'cart_courses': cart_courses,
                'all_bookmarks': all_bookmarks,
            })
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, course_id, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, course_id, *args, **kwargs):
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                Comment.objects.create(
                    user = request.user,
                    media_id = self.course.id,
                    media_type = 'course',
                    message = form.cleaned_data['message'],
                    parent = form.cleaned_data['parent_id'])
                self.context['msg'] = 'success'
            else:
                self.context['msg'] = 'failed'
            return render(request, self.template_name, self.context)
        return redirect('academy:login')
