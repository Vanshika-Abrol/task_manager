from django.urls import path

from . import views

urlpatterns = [
    path('show', views.show_noti, name='show'),
    path('del', views.delete_noti, name='del'),
    path('hide', views.hide_noti, name='hide'),
]

