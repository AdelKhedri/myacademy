from django import forms
from .models import Profile, User


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input'}), required=False, label='نام')
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input'}), required=False, label='نام خانوادگی')
    username = forms.CharField(validators=[], widget=forms.TextInput(attrs={'class': 'input'}), required=False, label='نام کاربری')

    class Meta:
        model = Profile
        fields = ['aboute', 'picture']
        widgets = {
            'aboute': forms.Textarea(attrs={'class': 'input', 'style': 'height: auto;', 'rows': 5}),
            'picture': forms.FileInput(attrs={'class': 'input'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['username'].initial = self.user.username

    def save(self, commit = True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
            profile.save()
        return user

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.user.username != username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('نام کاربری تکراری است.')
        return username
