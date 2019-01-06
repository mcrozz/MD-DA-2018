"""analytics URL Configuration"""
from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('ping', views.ping),
    path('run', views.run),
]
