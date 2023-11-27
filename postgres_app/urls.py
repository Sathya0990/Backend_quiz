from django.contrib import admin
from django.urls import path,include
from .views import Registration,LoginAPIView

urlpatterns = [

    path("registration/", Registration.as_view(), name='registration'),
    path('login/', LoginAPIView.as_view(), name='login'),




]
