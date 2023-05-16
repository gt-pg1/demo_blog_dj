from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.index, name='main'),
    path('feed', views.FeedView.as_view(), name='feed'),
    path('feed/<slug:slug>', views.ContentView.as_view(), name='content'),
    path('feed/<slug:slug>/edit', views.UpdateContentView.as_view(), name='update'),
    path('feed/<slug:slug>/unpublish', views.unpublish_content, name='unpublish'),
    path('feed/<slug:slug>/publish', views.publish_content, name='publish'),
    path('feed/<slug:slug>/delete_comment/<int:pk>', views.delete_comment, name='delete_comment'),
    path('<str:username>/my_content/', views.MyFeedView.as_view(), name='my_content'),
    path('create', views.CreateContentView.as_view(), name='create_content'),
    path('signup', views.UserSignUpView.as_view(), name='signup'),
    path('login', views.UserLogInView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('edit', views.UserEditView.as_view(), name='user_edit'),
    path('change_password', views.PasswordChangeView.as_view(), name='password_change'),
    path('<path:path>/', RedirectView.as_view(url='/%(path)s', permanent=True)),
]
