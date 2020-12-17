from accounts.models import UserProfileInfo
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()
non_allowed_usernames = ['abc', 'admin']

class RegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label= 'Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'user-password'
            }
        )
    )
    password2 = forms.CharField(
        label = 'Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'user-confirm-password'
            }
        )
    )
    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username__iexact=username)
        if username in  non_allowed_usernames:
            raise forms.ValidationError('This is an invalid username')
        if qs.exists():
            raise forms.ValidationError('This is an invalid username')

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError('This is email has been used')

        return email

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'user-password'
            }
        )
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username__iexact=username)

        if not qs.exists():
            raise forms.ValidationError('This is an invalid user')

        return username

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta():
        model = User
        fields = ('username','password','email')

class UserProfileInfoForm(forms.ModelForm):
    class Meta():
         model = UserProfileInfo
         fields = ('nama','foto_profil')