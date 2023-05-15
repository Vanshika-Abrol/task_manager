from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def show_noti(request):
    return HttpResponse("you are at show")
def delete_noti(request):
    return HttpResponse("you are at delete")
def hide_noti(request):
    return HttpResponse("you are at hide")