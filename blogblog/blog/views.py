from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, ListView, DetailView, CreateView, UpdateView

from .forms import UserSignUpForm, UserLogInForm, CommentForm, ContentForm, UserEditForm, UserPasswordChangeForm
from .models import Content, Comment


def index(request):
    return redirect('feed')


class PaginationRedirectMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and request.GET.get('page'):
            next_url = request.get_full_path()
            login_url = '{}?next={}'.format(reverse('login'), next_url)
            return redirect(login_url)
        return super().dispatch(request, *args, **kwargs)


class ContentRedirectMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            next_url = request.build_absolute_uri()
            login_url = f"{reverse('login')}?next={next_url}"
            return redirect(login_url)
        return super().dispatch(request, *args, **kwargs)


class UserSignUpView(FormView):
    template_name = 'blog/signup.html'
    form_class = UserSignUpForm

    def get_success_url(self):
        return reverse('feed')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        next_url = self.request.GET.get('next', reverse('feed'))
        return redirect(next_url)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


class UserLogInView(LoginView):
    template_name = 'blog/login.html'
    authentication_form = UserLogInForm

    def get_success_url(self):
        return reverse('feed')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        username = User.objects.get(email=email).username
        user = authenticate(self.request, username=username, password=password)
        if user is not None and user.is_authenticated:
            login(self.request, user)
            return redirect(self.request.GET.get('next', reverse('main')))
        else:
            form.add_error('email', 'Incorrect email or password')
            return self.form_invalid(form)


class UserEditView(View):
    template_name = 'blog/user_edit.html'
    user_form_class = UserEditForm
    password_form_class = UserPasswordChangeForm

    def get_success_url(self):
        return reverse('user_edit')

    def get(self, request, *args, **kwargs):
        user = request.user
        user_form = self.user_form_class(instance=user)
        password_form = self.password_form_class(user=user)
        return render(request, self.template_name, {'user_form': user_form, 'password_form': password_form})

    def post(self, request, *args, **kwargs):
        if 'save_user' in request.POST:
            user_form = self.user_form_class(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect(self.get_success_url())
            else:
                errors = user_form.errors
                if 'username' in errors:
                    messages.error(request, errors['username'])
                if 'first_name' in errors:
                    messages.error(request, errors['first_name'])
                if 'last_name' in errors:
                    messages.error(request, errors['last_name'])
                if 'phone' in errors:
                    messages.error(request, errors['phone'])

        if 'change_password' in request.POST:
            password_form = self.password_form_class(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been changed successfully.')
                return redirect(self.get_success_url())
            else:
                errors = password_form.errors
                if 'old_password' in errors:
                    messages.error(request, errors['old_password'])
                if 'new_password2' in errors:
                    messages.error(request, errors['new_password2'])
                return redirect(self.get_success_url())

        return redirect(self.get_success_url())


class FeedView(PaginationRedirectMixin, ListView):
    model = Content
    template_name = 'blog/feed.html'
    context_object_name = 'contents'
    login_url = 'login'
    paginate_by = 3

    def get_queryset(self):
        queryset = self.model.objects.filter(is_published=True).order_by('-date_time_create')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_page'] = context['page_obj'].number
        context['username'] = self.request.user.username
        return context


class MyFeedView(LoginRequiredMixin, FeedView):
    def get_queryset(self):
        queryset = self.model.objects.filter(author=self.request.user.author).order_by('-date_time_create')
        return queryset


class ContentView(ContentRedirectMixin, DetailView):
    model = Content
    template_name = 'blog/content.html'
    context_object_name = 'content'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.all()
        context['form'] = CommentForm()
        context['feed_page'] = self.request.GET.get('page')
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            content = self.get_object()
            comment = form.save(commit=False)
            comment.content = content
            comment.author = request.user.author
            comment.save()
            return redirect('content', slug=self.get_object().slug)
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context)


def delete_comment(request, slug, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user.author)
    comment.delete()
    return redirect('content', slug=slug)


class BaseContentView(LoginRequiredMixin, View):
    model = Content
    template_name = None
    form_class = ContentForm
    success_url = None

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user.author)

    def get_success_url(self):
        return reverse('content', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        form.instance.author = self.request.user.author
        return super().form_valid(form)


class CreateContentView(BaseContentView, CreateView):
    template_name = 'blog/create.html'


class UpdateContentView(BaseContentView, UpdateView):
    template_name = 'blog/update.html'


def change_content_status(request, slug, publish):
    content = get_object_or_404(Content, slug=slug, author=request.user.author)

    if publish:
        content.publish()
    else:
        content.unpublish()

    next_url = request.GET.get('next', 'feed')
    return redirect(next_url)


def unpublish_content(request, slug):
    return change_content_status(request, slug, False)


def publish_content(request, slug):
    return change_content_status(request, slug, True)
