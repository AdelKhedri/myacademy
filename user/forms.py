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


class PasswordChangeForm(forms.Form):
    last_password = forms.CharField(max_length=100, label='پسورد قبلی', widget=forms.PasswordInput)
    new_password1 = forms.CharField(
        max_length=100, label='پسورد جدید',
        widget=forms.PasswordInput,
        help_text= 'پسورد باید ترکیبی از متن و عدد و بیشتر از ۷ کاراکتر باشد.'
        )
    new_password2 = forms.CharField(max_length=100, label='تکرار پسورد', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data['new_password1']
        new_password2 = cleaned_data['new_password2']
        last_password = cleaned_data['last_password']

        if not new_password1 or not last_password or new_password1 != new_password2 or len(new_password1) < 7:
            raise forms.ValidationError('پسورد باید ترکیبی از متن و عدد و بیشتر از ۷ کاراکتر باشد.')
        elif not self.user.check_password(self.cleaned_data['last_password']):
            raise forms.ValidationError('پسورد قبلی اشتباه است.')
        return cleaned_data

    def save(self, commit = True):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user
