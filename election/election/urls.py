from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('voting.urls')),  # This connects your app
    path('otp-form/', views.otp_form, name='otp_form'),
    path('send-otp/', views.send_otp, name='send_otp'),
]
