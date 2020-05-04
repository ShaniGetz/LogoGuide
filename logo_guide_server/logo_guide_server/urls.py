from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from algorithm import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^logoguide/$', views.LogoGuide.as_view())
]