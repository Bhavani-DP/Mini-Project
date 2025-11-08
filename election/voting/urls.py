from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('aadhaar/', views.verify_aadhaar, name='verify_aadhaar'),
    path('send_otp/', views.send_otp, name='send_otp'),

]