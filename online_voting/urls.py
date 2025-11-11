from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from voting import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('otp-form/', include('voting.urls')), 
    path('', include('voting.urls')),   
    path('accounts/', include('accounts.urls')),  # Login
    path('send_otp/', views.send_otp, name='send_otp'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
