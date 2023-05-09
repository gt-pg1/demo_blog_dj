from collections import OrderedDict

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from tinymce.widgets import TinyMCE

from .helpers import to_latin
from .models import Comment, Content


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

        # Saving data for the Author model occurs through the post_save signal in signal.py
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


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3})
        }


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ('title', 'text')



