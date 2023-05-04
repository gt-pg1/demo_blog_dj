from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='main'),
    # path('feed', login_required(views.IndexView.as_view()), name='feed'),
    path('feed', views.FeedView.as_view(), name='feed'),
    path('signup', views.UserSignUpView.as_view(), name='signup'),
    path('login', views.UserLogInView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout')
]