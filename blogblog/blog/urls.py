from . import views
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path('', views.index, name='main'),
    path('signup', views.UserSignUpView.as_view(), name='signup'),
    path('login', views.UserLogInView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout')
]