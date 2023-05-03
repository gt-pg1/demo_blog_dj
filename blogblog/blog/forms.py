from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AuthorCreationForm(UserCreationForm):
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
