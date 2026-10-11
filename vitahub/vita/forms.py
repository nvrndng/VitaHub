from django import forms
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label='Подтверждение пароля'
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'password',
        )

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Пользователь с таким email уже зарегистрирован.'
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if (
            password
            and password_confirm
            and password != password_confirm
        ):
            raise forms.ValidationError(
                'Пароли не совпадают.'
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            Profile.objects.create(
                user=user
            )

        return user


class ProfileForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=150,
        required=False,
        label='Имя'
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        label='Фамилия'
    )

    email = forms.EmailField(
        label='Email'
    )

    class Meta:
        model = Profile
        fields = (
            'nickname',
            'photo',
            'phone',
            'about',
        )

        labels = {
            'nickname': 'Никнейм',
            'photo': 'Фотография',
            'phone': 'Телефон',
            'about': 'О себе',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')

        super().__init__(*args, **kwargs)

        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['email'].initial = user.email

    def save(self, user, commit=True):
        profile = super().save(commit=commit)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return profile