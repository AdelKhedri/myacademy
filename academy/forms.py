from django import forms
from .models import Course, Seasion, Comment


class CourseForm(forms.ModelForm):
    related_course = forms.ModelMultipleChoiceField(
        required=False,
        queryset = Course.objects.filter(is_active = True),
        widget = forms.SelectMultiple(attrs={'class': 'tpd-select2 form-select'}))

    class Meta:
        model = Course
        fields = ['name', 'category', 'description', 'price', 'price_with_discount', 'tax', 'related_course', 'thumbnail', 'time', 'difficulty_level', 'is_certificate', 'trailer', 'is_askable',]

    def save(self, teacher = None, commit = True):
        form = super().save(False)
        form.teacher = teacher
        related_course = self.cleaned_data['related_course']
        category = self.cleaned_data['category']

        if commit:
            form.save()
            form.related_course.set(related_course)
            form.category.set(category)
            form.save()
        return form


class SeasionAddForm(forms.ModelForm):
    class Meta:
        model = Seasion
        fields = ['title']


SeasionFormSet = forms.formset_factory(SeasionAddForm, extra=2)

class CommentForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(), label='پیام')
    parent_id = forms.ModelChoiceField(
        label='ایدی والد',
        widget=forms.HiddenInput(),
        queryset=Comment.objects.filter(media_type = 'course', ),
        required=False
        )
