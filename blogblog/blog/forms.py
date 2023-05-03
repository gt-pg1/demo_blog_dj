from datetime import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Author
import re
from transliterate import translit
from collections import OrderedDict


def to_latin(string):
    if re.match('^[A-Za-z0-9_-]*$', string):
        return string
    return translit(string, 'ru', reversed=True)


class AdminUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Required'
    )
    phone = forms.CharField(
        required=False
    )
    first_name = forms.CharField(
        required=True,
        help_text='Required. 150 characters or fewer.'
    )
    last_name = forms.CharField(
        required=True,
        help_text='Required. 150 characters or fewer.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'first_name', 'last_name', 'password1', 'password2')


class UserSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True, help_text='Required. 150 characters or fewer.')
    last_name = forms.CharField(required=True, help_text='Required. 150 characters or fewer.')
    email = forms.EmailField(required=True, help_text='Required')
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()
    agree_to_terms = forms.BooleanField(required=True, label='Agree to processing of personal data', initial=True)

    class Meta(UserCreationForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agree_to_terms'].widget.attrs.update({'class': 'form-check-input'})

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('agree_to_terms'):
            raise forms.ValidationError('You must agree to the processing of personal data')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        first_name = to_latin(self.cleaned_data['first_name'])
        last_name = to_latin(self.cleaned_data['last_name'])

        username = f"{first_name}-{last_name}-{user.id + 100001}"
        user.username = username.lower()

        if commit:
            user.save()

        return user


class UserLogInForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Arranging form fields to make HTML more compact
        del self.fields['username']
        fields = OrderedDict()
        fields.update({'email': forms.EmailField()})
        fields.update(self.fields)
        self.fields = fields

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise ValidationError("User with this email was not found")
            else:
                if not user.check_password(password):
                    raise ValidationError("Incorrect password")
                if not user.is_active:
                    raise ValidationError("User is inactive")
        print(email, password)

        return self.cleaned_data