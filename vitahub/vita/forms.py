from django import forms
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')


    def clean_email(self):
        email = self.cleaned_data.get['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован')

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают!')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            Profile.objects.create(user=user)

        return user