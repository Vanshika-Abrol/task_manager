from django.urls import path, include

from . import views

urlpatterns = [
    path('create_task', views.create_task,name='create_task'),
    path('update_task', views.update_task,name='update_task'),
    path('delete_task', views.delete_task,name='delete_task'),
    path('view_filter', views.view_filter,name='view_filter'),
    path('search', views.search,name='search'),
    path('send_request', views.send_request,name='send_request'),
    path('accept_request', views.accept_request,name='accept_request'),
    path('reject_request', views.reject_request,name='reject_request')
]


