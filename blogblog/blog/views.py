from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import UserSignUpForm, UserLogInForm


def index(request):
    return HttpResponse('<p>Main</p>')


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
