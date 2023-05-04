from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import F
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from .forms import UserSignUpForm, UserLogInForm
from .models import Content


def index(request):
    return render(request, 'blog/base.html')


class UserSignUpView(FormView):
    template_name = 'blog/signup.html'
    form_class = UserSignUpForm
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class UserLogInView(LoginView):
    template_name = 'blog/login.html'
    authentication_form = UserLogInForm
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        username = User.objects.get(email=email).username
        user = authenticate(self.request, username=username, password=password)
        if user is not None and user.is_authenticated:
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            form.add_error('email', 'Incorrect email or password')
            return self.form_invalid(form)

    def get_success_url(self):
        return self.success_url


class FeedView(LoginRequiredMixin, ListView):
    model = Content
    template_name = 'blog/feed.html'
    context_object_name = 'contents'
    login_url = 'login'
    paginate_by = 3

    def get_queryset(self):
        return self.model.objects.filter(is_published=True).order_by('-date_time_create')
