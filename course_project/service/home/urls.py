"""home URL Configuration"""
from django.contrib import admin
from django.urls import include, path
from . import views


urlpatterns = [
    path('', views.index),
    path('wait/', views.wait),
    path('result/<genre>', views.genre_result),
]
