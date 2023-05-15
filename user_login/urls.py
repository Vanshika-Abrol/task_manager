from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('create_profile', views.create_profile, name='create_profile'),
    path('add_profile_photo', views.add_profile_photo, name='add_profile_photo'),
    path('invite_user', views.invite_user, name='invite_user')
]
