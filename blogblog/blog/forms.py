from collections import OrderedDict

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .helpers import to_latin
from .models import Comment, Content, Author


class LowercaseEmailMixin:
    """
    Mixin for ensuring that the email field is always saved in lowercase.

    This mixin provides a clean_email method that converts the email field value to lowercase.
    It can be used in Django forms or model forms to enforce lowercase email storage.
    """

    def clean_email(self):
        """
        Converts the email field value to lowercase.

        Returns:
            str: The lowercase version of the email.
        """
        email = self.cleaned_data['email']
        return email.lower()


class AdminUserCreationForm(LowercaseEmailMixin, UserCreationForm):
    """
    A custom user creation form for the admin panel.
    This is necessary because the base User model is extended by the Author model.

    This form extends the default `UserCreationForm` and adds additional fields and functionality.
    It includes the `LowercaseEmailMixin` to ensure that the email is always stored in lowercase.

    Attributes:
        email (forms.EmailField): The email field for the user. Required.
        phone (forms.CharField): The phone field for the user. Optional.
        first_name (forms.CharField): The first name field for the user. Required.
        last_name (forms.CharField): The last name field for the user. Required.

    Meta:
        model (User): The User model to be used for the form.
        fields (tuple): The fields to be included in the form.

    """
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
        fields = (
            'username',
            'email',
            'phone',
            'first_name',
            'last_name',
            'password1',
            'password2'
        )


class UserSignUpForm(LowercaseEmailMixin, UserCreationForm):
    """
    A form for user sign-up, based on UserCreationForm with additional fields and validation.

    Inherits from UserCreationForm and includes fields for first name, last name, email,
    password, and agreement to terms. Provides validation for the agreement to terms field
    and custom save method to handle data processing and user creation.

    Attributes:
        first_name (CharField): Field for the user's first name.
        last_name (CharField): Field for the user's last name.
        email (EmailField): Field for the user's email address.
        password1 (PasswordInput): Field for the user's password.
        password2 (PasswordInput): Field to confirm the user's password.
        agree_to_terms (BooleanField): Field to indicate the user's agreement to the terms.

    Meta:
        Inherits the Meta class from UserCreationForm, specifying the fields to include in the form.

    Methods:
        __init__(self, *args, **kwargs): Initializes the UserSignUpForm instance.
            Updates the 'agree_to_terms' field widget attributes.

        clean(self): Performs additional form validation.
            Checks if the user has agreed to the processing of personal data.

        save(self, commit=True): Saves the user data to the database.
            Overrides the default save method to include additional processing steps,
            such as setting the email, generating a username, and saving the user.

    """
    first_name = forms.CharField(
        required=True,
        help_text='Required. 150 characters or fewer.'
    )
    last_name = forms.CharField(
        required=True,
        help_text='Required. 150 characters or fewer.'
    )
    email = forms.EmailField(
        required=True,
        help_text='Required'
    )
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()
    agree_to_terms = forms.BooleanField(
        required=True,
        label='Agree to processing of personal data',
        initial=True
    )

    class Meta(UserCreationForm.Meta):
        fields = [
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]

    def __init__(self, *args, **kwargs):
        """
        Initializes a UserSignUpForm instance.

        It modifies the form by adding a checkbox widget for agreeing to the terms.
        """
        super().__init__(*args, **kwargs)
        self.fields['agree_to_terms'].widget.attrs.update({'class': 'form-check-input'})

    def clean(self):
        """
        Cleans and validates the form data.

        This method is called during form validation.
        It ensures that the 'agree_to_terms' checkbox is checked before allowing the form to be submitted.
        If the checkbox is not checked, a validation error is raised.

        Returns:
            dict: A dictionary containing the cleaned form data.

        Raises:
            forms.ValidationError: If the 'agree_to_terms' checkbox is not checked.

        """
        cleaned_data = super().clean()
        if not cleaned_data.get('agree_to_terms'):
            raise forms.ValidationError('You must agree to the processing of personal data')
        return cleaned_data

    def save(self, commit=True):
        """
        Saves the user data to the database.

        Overrides the default save method to include additional processing steps,
        such as setting the email, generating a username, and saving the user.

        When a new user is saved in the database, an entry in the Author table will appear automatically.
        The create_author(post_save) function for this is written in the "blog/signal.py".

        Args:
            commit (bool, optional): Determines whether to save the user to the database. Defaults to True.

        Returns:
            User: The saved user instance.
        """

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


class UserLogInForm(LowercaseEmailMixin, AuthenticationForm):
    """
    Form class for user login.

    Inherits from LowercaseEmailMixin and AuthenticationForm.

    Attributes:
        email (EmailField): Email field for user login.

    Methods:
        __init__: Initializes the form instance.
        clean: Performs form validation and checks if the user with the provided email and password exists, and if
               the user is active.

    """

    email = forms.EmailField(widget=forms.EmailInput())

    def __init__(self, *args, **kwargs):
        """
        Initializes the UserLogInForm instance.

        Removes the 'username' field from the form and rearranges the fields to make the HTML templates more compact.
        """

        super().__init__(*args, **kwargs)

        del self.fields['username']

        fields = OrderedDict()
        fields['email'] = forms.EmailField()
        fields.update(self.fields)
        self.fields = fields

    def clean(self):
        """
        Performs form validation and checks if the user with the provided email and password exists and is active.

        Raises:
            ValidationError: If the user with the provided email was not found, the password is incorrect,
                             or the user is inactive.

        Returns:
            dict: Cleaned form data.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise ValidationError("User with this email was not found")

            if not user.check_password(password):
                raise ValidationError("Incorrect password")

            if not user.is_active:
                raise ValidationError("User is inactive")

        return cleaned_data


class UserEditForm(forms.ModelForm):
    """
    Form for editing user profile information.

    Fields:
        first_name (CharField): First name of the user.
        last_name (CharField): Last name of the user.
        email (EmailField): Email address of the user.
        phone (CharField): Phone number of the user.
        username (CharField): Username of the user.

    Meta:
        model (User): The model associated with the form.
        fields (list): The fields to include in the form.

    Attributes:
        author (Author): The associated author instance, if available.

    Methods:
        __init__(self, *args, **kwargs): Initializes the form instance.
        save(self, commit=True): Saves the form data and updates the associated author instance.

    """
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(widget=forms.HiddenInput)
    phone = forms.CharField(max_length=25, required=False)
    username = forms.CharField()

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'phone']

    def __init__(self, *args, **kwargs):
        """
        Initializes the form instance.

        The __init__ method is responsible for initializing the form instance.
        It sets the initial values for form fields and retrieves the associated author instance, if available.

        If the 'instance' keyword argument is provided, it retrieves the associated author from the 'Author' model
        using the 'user' foreign key relationship with the provided user instance.
        If an associated author exists, the 'phone' field is initialized with the author's phone value.

        If the 'Author.DoesNotExist' exception is raised during the retrieval process, it means that there is no
        associated author for the user instance, and the 'phone' field is left untouched.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Attributes:
            author (Author): The associated author instance, if available.
        """
        super().__init__(*args, **kwargs)
        self.author = None
        instance = kwargs.get('instance')
        if instance:
            try:
                self.author = Author.objects.get(user=instance)
                self.fields['phone'].initial = self.author.phone
            except Author.DoesNotExist:
                pass

    def save(self, commit=True):
        """
        Saves the form data and updates the associated author instance.

        Args:
            commit (bool): Flag indicating whether to commit the changes to the database. Defaults to True.

        Returns:
            User: The saved user instance.
        """
        user = super().save(commit=commit)
        if commit and self.author:
            self.author.phone = self.cleaned_data['phone']
            self.author.save()
        return user


class UserPasswordChangeForm(PasswordChangeForm):

    """
    !!!THIS METHOD IS NOT USED IN THE WEB APP CURRENTLY. !!!
    !!!IT WILL BE SAVED UNTIL THE LAYOUT AND DESIGN OF THE SITE IS ADDED!!!
    A form for changing the user's password.

    Fields:
        old_password (CharField): The field for the old password.
        new_password1 (CharField): The field for the new password.
        new_password2 (CharField): The field for confirming the new password.

    The 'UserPasswordChangeForm' class provides a form for users to change their password.
    It extends Django's built-in 'PasswordChangeForm' class and adds additional customization.

    Meta:
        model (User): The User model class associated with the form.
        fields (tuple): The fields to include in the form.

    """
    old_password = forms.PasswordInput(attrs={'type': 'password'})
    new_password1 = forms.PasswordInput(attrs={'type': 'password'})
    new_password2 = forms.PasswordInput(attrs={'type': 'password'})

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class CommentForm(forms.ModelForm):
    """
    Form for creating or updating a comment.

    Serves as a model form for the Comment model.
    Fields:
    - text (str): The text content of the comment.

    Meta:
        model (Comment): The Comment model associated with the form.
        fields (list): The fields to include in the form, which are 'text'.
        widgets (dict): The widgets to use for each form field, where 'text' field
            is rendered as a Textarea widget with 3 rows.
    """
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': forms.Textarea(attrs={'rows': 3})}


class ContentForm(forms.ModelForm):
    """
    Form for creating or updating content.

    Serves as a model form for the Content model.
    Fields:
    - title (str): The title of the content.
    - text (str): The text content of the content.

    Meta:
        model (Content): The Content model associated with the form.
        fields (list): The fields to include in the form, which are 'title' and 'text'.
    """
    class Meta:
        model = Content
        fields = ('title', 'text')
