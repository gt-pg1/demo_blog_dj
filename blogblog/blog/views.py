from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, DetailView, CreateView

from .forms import UserSignUpForm, UserLogInForm, CommentForm, ContentForm
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
    success_url = reverse_lazy('feed')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        next_url = self.request.GET.get('next', reverse('feed'))
        return redirect(next_url)


class UserLogInView(LoginView):
    template_name = 'blog/login.html'
    authentication_form = UserLogInForm

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

    def get_success_url(self):
        return self.success_url


class FeedView(PaginationRedirectMixin, ListView):
    model = Content
    template_name = 'blog/feed.html'
    context_object_name = 'contents'
    login_url = 'login'
    paginate_by = 3

    def get_queryset(self):
        return self.model.objects.filter(is_published=True).order_by('-date_time_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_page'] = context['page_obj'].number
        return context


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


class CreateContentView(LoginRequiredMixin, CreateView):
    model = Content
    template_name = 'blog/create.html'
    form_class = ContentForm
    success_url = reverse_lazy('feed')

    def form_valid(self, form):
        form.instance.author = self.request.user.author
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('content', kwargs={'slug': self.object.slug})
