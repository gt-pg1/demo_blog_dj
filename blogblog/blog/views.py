from datetime import timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, ListView, DetailView, CreateView, UpdateView

from .forms import UserSignUpForm, UserLogInForm, CommentForm, ContentForm, UserEditForm, UserPasswordChangeForm
from .models import Content, Comment


def index(request):
    """
    Redirects the user to the 'feed' URL.

    This view function redirects the user to the 'feed' URL, which represents the main feed page of the application.
    """
    return redirect('feed')


class AuthenticationRedirectMixin:
    """
    Mixin that redirects unauthenticated users to the login page.

    Methods:
        - dispatch(request, *args, **kwargs): Redirects unauthenticated users to the login page.

    Args:
        request (HttpRequest): The HTTP request object.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        HttpResponse: The response object.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Redirects unauthenticated users to the login page.

        This method is called when a request is made to the associated view. It checks if the user is not authenticated.
        If the user is unauthenticated, it redirects them to the login page with the 'next' parameter set to the current URL.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The response object.

        """

        if not request.user.is_authenticated:
            if 'page' in request.GET:
                next_url = request.get_full_path()
                print('page', next_url)
                login_url = f"{reverse('login')}?next={next_url}"
                return redirect(login_url)

            elif 'next' in request.GET:
                next_url = request.build_absolute_uri()
                print('next', next_url)
                login_url = f"{reverse('login')}?next={next_url}"
                return redirect(login_url)

        return super().dispatch(request, *args, **kwargs)


class SuccessUrlRedirectMixin:
    """
    Mixin that redirects authenticated users to a specified success URL.

    Methods:
        - dispatch(request, *args, **kwargs): Handles the request dispatching.

    Args:
        request (HttpRequest): The request object.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        HttpResponse: The response for the request dispatching.

    Note:
        This mixin should be applied only if the `success_url` attribute is defined in the class.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Handles the request dispatching.

        If the user is already authenticated and the `success_url` attribute is defined,
        it redirects them to the success URL. Otherwise, it proceeds with the default dispatching behavior.

        Args:
            request (HttpRequest): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The response for the request dispatching.
        """

        if request.user.is_authenticated and hasattr(self, 'success_url'):
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)


class UserSignUpView(SuccessUrlRedirectMixin, FormView):
    """
    View for user sign-up.

    Renders the sign-up form and handles form submission. Upon successful form submission,
    it creates a new user, logs them in, and redirects them to the desired page.

    Attributes:
        template_name (str): The name of the template used for rendering the sign-up form.
        form_class (Form): The form class to be used for user sign-up.
        success_url (str): The URL to redirect to after successful sign-up.

    Methods:
        form_valid(form): Handles the form submission when it is valid.
        dispatch(request, *args, **kwargs): Handles the request dispatching.

    """

    template_name = 'blog/signup.html'
    form_class = UserSignUpForm
    success_url = reverse_lazy('feed')

    def form_valid(self, form):
        """
        Handles the form submission when it is valid.

        Creates a new user, logs them in, and redirects them to the desired page.

        Args:
            form (Form): The validated form.

        Returns:
            HttpResponse: The response for redirecting the user to the desired page.

        """

        user = form.save()
        login(self.request, user)
        next_url = self.request.GET.get('next', reverse('feed'))
        return redirect(next_url)


class UserLogInView(SuccessUrlRedirectMixin, LoginView):
    """
    View for user login.

    Renders the login form and handles form submission. Upon successful form submission,
    it authenticates the user, logs them in, and redirects them to the desired page.

    Attributes:
        template_name (str): The name of the template used for rendering the login form.
        authentication_form (Form): The form class to be used for user authentication.

    Methods:
        get_success_url(): Returns the URL to redirect to after successful login.
        dispatch(request, *args, **kwargs): Handles the request dispatching.
        form_valid(form): Handles the form submission when it is valid.

    """

    template_name = 'blog/login.html'
    authentication_form = UserLogInForm
    success_url = reverse_lazy('feed')

    def form_valid(self, form):
        """
        Handles the validation of the login form.

        Retrieves the email and password from the form's cleaned data.
        Attempts to retrieve the username associated with the given email.
        Authenticates the user with the provided username and password.
        If the user is successfully authenticated, logs in the user and redirects to the 'main' page.
        Otherwise, the form is considered invalid.

        Args:
            form (UserLogInForm): The form instance.

        Returns:
            HttpResponseRedirect: A redirect response to the 'main' page if the user is authenticated.
            HttpResponse: The rendered form with errors if the user is not authenticated.
        """

        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        username = User.objects.get(email=email).username
        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        if user is None:
            form.add_error(None, 'Authentication failed')
            return self.form_invalid(form)
        elif user.is_authenticated:
            login(self.request, user)
            return redirect(self.request.GET.get('next', reverse('main')))
        else:
            return self.form_invalid(form)


class UserEditView(View):
    """
    A view for editing user profile and changing password.

    This view allows users to edit their profile information and change their password on the one page.
    It uses the UserEditForm and PasswordChangeForm to handle form validation and processing.
    After successful profile update or password change, the user is redirected to the 'user_edit' page.

    Attributes:
        template_name (str): The name of the template to be rendered.
        user_form_class (Form): The form class for editing user profile information.
        password_form_class (Form): The form class for changing the user's password.
        success_url (str): The URL to redirect to after successful form submission.

    Methods:
        get(request, *args, **kwargs): Handles GET requests and renders the user edit page with the forms.
        post(request, *args, **kwargs): Handles POST requests and processes the submitted forms.
    """

    template_name = 'blog/user_edit.html'
    user_form_class = UserEditForm
    password_form_class = UserPasswordChangeForm
    success_url = reverse_lazy('user_edit')

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests and render the user edit page.

        Retrieves the current user, creates instances of user_form and password_form,
        and renders the user edit template with the forms as context.
        In particular, it is necessary to display the current user data.

        Args:
            request (HttpRequest): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The rendered user edit page.
        """

        user = request.user
        user_form = self.user_form_class(instance=user)
        password_form = self.password_form_class(user=user)
        return render(
            request,
            self.template_name,
            {'user_form': user_form, 'password_form': password_form}
        )

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests and process the submitted forms.

        Checks the action in the POST data to determine whether it's a user profile update or password change.
        Validates the submitted forms and performs the corresponding actions.
        If the forms are valid, the user profile is updated or the password is changed,
        and the user is redirected to the success URL.
        If there are form errors, error messages are added to the messages framework.

        Args:
            request (HttpRequest): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The response to be returned, either a redirect or the success URL.
        """

        if 'save_user' in request.POST:
            user_form = self.user_form_class(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect(self.success_url)
            else:
                errors = user_form.errors
                for field in errors:
                    messages.error(request, errors[field])

        if 'change_password' in request.POST:
            password_form = self.password_form_class(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been changed successfully.')
                return redirect(self.success_url)
            else:
                errors = password_form.errors
                for field in errors:
                    messages.error(request, errors[field])

        return redirect(self.success_url)

    def dispatch(self, request, *args, **kwargs):
        """
        Handle the request by checking if the user is authenticated.

        If the user is not authenticated, it redirects to the login page.
        If the user is authenticated, it allows the request to be dispatched to the appropriate method.

        Args:
            request (HttpRequest): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The response to be returned, either a redirect or the dispatched method's response.
        """

        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        return super().dispatch(request, *args, **kwargs)


class FeedView(AuthenticationRedirectMixin, ListView):
    """
    A view for displaying the feed content.

    This view inherits from the AuthenticationRedirectMixin and ListView classes.
    It displays the feed content to authenticated users and redirects anonymous users to the login page.

    Attributes:
        model (Model): The model class to retrieve data from.
        template_name (str): The name of the template to be rendered.
        context_object_name (str): The name of the variable to use in the template for the list of objects.
        login_url (str): The URL to redirect to for anonymous users.
        paginate_by (int): The number of items to display per page.

    Methods:
        get_queryset(): Returns the queryset of feed content to be displayed.
        get_context_data(**kwargs): Adds additional context data to be used in the template.
        get_template_names(): Returns the template names based on the request type.
    """

    model = Content
    context_object_name = 'contents'
    login_url = 'login'
    paginate_by = 20

    def get_queryset(self):
        """
        Returns the queryset of feed content to be displayed.

        Filters the content by 'is_published' and orders it by the 'date_time_create' field in descending order.
        Counts the number of comments on a post

        Returns:
            QuerySet: The filtered and ordered queryset of feed content.
        """

        queryset = self.model.objects.filter(is_published=True).order_by('-date_time_create')
        queryset = queryset.annotate(comment_count=Count('comment'))
        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds additional context data to be used in the template.

        Adds the current number of feed page number to the context.
        This is necessary for the subsequent storage of the page number in the GET parameter of the link.

        The method also updates the `short_text` attribute of each content item
        in the `contents` queryset. It calls the `short_text` method of the `Content`
        model, which returns a shortened version of the article text.
        Adds the 'title' attribute to the context data.

        Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: The updated context data.
        """

        context = super().get_context_data(**kwargs)
        context['feed_page'] = context['page_obj'].number
        context['title'] = 'Feed — Demo Blog'
        for content in context['contents']:
            content.short_text = content.short_text(250)

        return context

    def get_template_names(self):
        """
        Returns the template names based on the request type.

        If the request is made via XMLHttpRequest (AJAX), it returns a partial template.
        Otherwise, it returns the regular feed template.

        Returns:
            list: The list of template names.
        """

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['blog/includes/partial_feed.html']
        return ['blog/feed.html']


class MyFeedView(LoginRequiredMixin, FeedView):
    """
    A view for displaying the feed content of the current user.

    This view inherits from the LoginRequiredMixin and FeedView classes.
    It requires the user to be authenticated and displays only their own feed content.

    Methods:
        get_queryset(): Returns the queryset of user's feed content to be displayed.
    """

    def get_queryset(self):
        """
        Returns the queryset of user's feed content to be displayed.

        Filters the content by the current user's author and orders it by the 'date_time_create' field in descending order.
        Counts the number of comments on a post

        Returns:
            QuerySet: The filtered and ordered queryset of user's feed content.
        """

        queryset = self.model.objects.filter(author=self.request.user.author).order_by('-date_time_create')
        queryset = queryset.annotate(comment_count=Count('comment'))
        return queryset

    def get_context_data(self, **kwargs):
        """
        Returns the context data for rendering the view.

        Adds the 'title' attribute to the context data.

        Returns:
            dict: The context data for rendering the view.
        """

        context = super().get_context_data(**kwargs)
        context['title'] = 'My Feed — Demo Blog'
        return context


class ContentView(AuthenticationRedirectMixin, DetailView):
    """
    This class-based view displays the detailed view of a content object and handles adding comments to the content.

    Inherits from:
        - ContentRedirectMixin: A mixin that handles a redirect if the user is not authorized.

    Attributes:
        model (Model): The model class representing the content objects.
        template_name (str): The name of the template used to render the content view.
        context_object_name (str): The name of the context variable containing the content object.

    Methods:
        get_context_data(self, **kwargs): Returns the context data for rendering the content view.
        post(self, request, *args, **kwargs): Handles the HTTP POST request for adding comments to the content.
    """

    model = Content
    template_name = 'blog/content.html'
    context_object_name = 'content'

    def get_context_data(self, **kwargs):
        """
        Returns the context data for rendering the content view, including the comment form,
        comments, comments count, and the page number from which the user accessed the content.

        Returns:
            dict: The context data.
        """

        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.all()
        context['comments_count'] = context['comments'].count()
        context['form'] = CommentForm()
        context['feed_page'] = self.request.GET.get('page')

        content = self.object
        queryset = self.get_queryset()
        prev_content = (
            queryset
            .filter(date_time_create__lt=content.date_time_create, is_published=True)
            .order_by('-date_time_create')
            .first()
        )

        next_content = (
            queryset
            .filter(date_time_create__gt=content.date_time_create, is_published=True)
            .order_by('date_time_create')
            .first()
        )

        context['prev_content'] = prev_content
        context['next_content'] = next_content
        context['has_prev_content'] = bool(prev_content)
        context['has_next_content'] = bool(next_content)

        return context

    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST request for adding comments to the content.
        Processes the page data to ensure the correct transfer of the last page number in the 'page' query parameter.

        Args:
            request (HttpRequest): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponseRedirect: The redirect response after adding a comment.
        """

        form = CommentForm(request.POST)
        content = self.get_object()
        page = self.request.GET.get('page')
        url = reverse('content', kwargs={'slug': content.slug})
        params = urlencode({'page': page}) if page else ''

        if form.is_valid():
            comment = form.save(commit=False)
            comment.content = content
            comment.author = request.user.author
            comment.save()

            return redirect(f"{url}?{params}")

        context = {
            'form': form,
            'content': content,
            'comments': content.comment_set.all(),
            'feed_page': page,
        }
        return redirect(f"{url}?{params}", context)


def delete_comment(request, slug, pk):
    """
    Deletes a comment based on the provided comment ID.
    Redirects to the content view after deleting the comment.

    Args:
        request (HttpRequest): The request object.
        slug (str): The slug of the content.
        pk (int): The primary key of the comment to delete.

    Returns:
        HttpResponseRedirect: The redirect response to the content view.

    Note:
        The function handles the page data to ensure correct transfer of the last page number
        in the 'page' GET parameter.
    """

    comment = get_object_or_404(Comment, pk=pk, author=request.user.author)
    comment.delete()

    page = request.GET.get('page')
    url = reverse('content', kwargs={'slug': slug})
    params = urlencode({'page': page}) if page else ''
    redirect_url = f"{url}?{params}"

    return redirect(redirect_url)


class CreateAuthorMixin(LoginRequiredMixin, View):
    """
    A mixin that restricts access to content creation and updating to the authenticated user who is the author.

    Inherits from:
        - LoginRequiredMixin: Ensures that the user is authenticated before accessing the view.
        - View: Provides the base implementation for class-based views.

    Attributes:
        - model (Model): The model associated with the content.
        - template_name (str): The name of the template used to render the view.
        - form_class (Form): The form class used for creating or updating content.
        - success_url (str): The URL to redirect to after successful creation or update of content.

    Methods:
        - get_queryset(): Returns a filtered queryset containing content owned by the current authenticated user (author).
        - get_success_url(): Returns the URL to redirect to after successful creation or update of content.
        - form_valid(form): Sets the author of the content to the current authenticated user before saving the form.
    """
    model = Content
    template_name = None
    form_class = ContentForm

    def get_queryset(self):
        """
        Returns a filtered queryset containing content owned by the current authenticated user (author).
        """

        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user.author)

    def get_success_url(self):
        """
        Returns the URL to redirect to after successful creation or update of content.
        """

        return reverse('content', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        """
        Sets the author of the content to the current authenticated user before saving the form.
        """

        form.instance.author = self.request.user.author
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        return super().dispatch(request, *args, **kwargs)


class CreateContentView(CreateAuthorMixin, CreateView):
    """
    A view that allows the authenticated user (author) to create new content.

    Inherits from:
        - CreateAuthorMixin: Restricts access to content creation to the authenticated user who is the author.
        - CreateView: Provides the functionality for creating new objects.

    Attributes:
        template_name (str): The name of the template used to render the view.
        cooldown_period (timedelta): The cooldown period between content submissions in minutes.
    """

    template_name = 'blog/article_form.html'
    cooldown_period = timedelta(minutes=10)

    def get_context_data(self, **kwargs):
        """
        Adds additional context data to be used in the template.

        Adds the page title and button text to the context.

        Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: The updated context data.
        """

        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Article'
        context['button_text'] = 'Create Article'
        return context

    def form_valid(self, form):
        """
        Handle the valid form submission.

        If the user is not a superuser and has submitted content within the cooldown period,
        display an error message and invalidate the form submission. Otherwise, associate
        the content with the author and save it to the database.

        Args:
            form (Form): The submitted form instance.

        Returns:
            HttpResponse: The response after form submission.
        """

        author = self.request.user.author
        if not self.request.user.is_superuser and author.date_time_last_post:
            cooldown_end = author.date_time_last_post + self.cooldown_period
            if cooldown_end > timezone.now():
                cooldown_remaining = (cooldown_end - timezone.now()).total_seconds() // 60
                message = f"You can post content again in {int(cooldown_remaining)} minutes."
                messages.error(self.request, message)
                return self.form_invalid(form)

        form.instance.author = author
        response = super().form_valid(form)

        author.date_time_last_post = timezone.now()
        author.save()

        return response


class UpdateContentView(CreateAuthorMixin, UpdateView):
    """
    A view that allows the authenticated user (author) to update existing content.

    Inherits from:
        - CreateAuthorMixin: Restricts access to content updating to the authenticated user who is the author.
        - UpdateView: Provides the functionality for updating existing objects.

    Attributes:
        template_name (str): The name of the template used to render the view.
    """

    template_name = 'blog/article_form.html'

    def get_context_data(self, **kwargs):
        """
        Adds additional context data to be used in the template.

        Adds the page title and button text to the context.

        Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: The updated context data.
        """

        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Article'
        context['button_text'] = 'Update Article'
        return context



def change_content_status(request, slug, publish):
    """
    Change the status of a content item (publish or unpublish) based on the provided slug.

    Args:
        - request (HttpRequest): The HTTP request object.
        - slug (str): The slug of the content item.
        - publish (bool): Boolean flag indicating whether to publish (True) or unpublish (False) the content.

    Returns:
        - HttpResponse: A redirect response to the specified next URL.
    """

    content = get_object_or_404(Content, slug=slug, author=request.user.author)

    if publish:
        content.publish()
    else:
        content.unpublish()

    next_url = request.GET.get('next', 'feed')
    return redirect(next_url)


def unpublish_content(request, slug):
    """
    Unpublish a content item based on the provided slug.

    Args:
        - request (HttpRequest): The HTTP request object.
        - slug (str): The slug of the content item.

    Returns:
        - HttpResponse: A redirect response to the specified next URL.
    """

    return change_content_status(request, slug, False)


def publish_content(request, slug):
    """
    Publish a content item based on the provided slug.

    Args:
        - request (HttpRequest): The HTTP request object.
        - slug (str): The slug of the content item.

    Returns:
        - HttpResponse: A redirect response to the specified next URL.
    """

    return change_content_status(request, slug, True)
