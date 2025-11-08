from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('confirm_otp/', views.confirm_otp, name='confirm_otp'),
    path('cast_vote/', views.cast_vote, name='cast_vote'),
    path('submit_vote/', views.submit_vote, name='submit_vote'),
    path('confirm_vote/', views.confirm_vote, name='confirm_vote'),
    path('finalize_vote/', views.finalize_vote, name='finalize_vote'),
     path('aadhaar/', views.verify_aadhaar, name='verify_aadhaar'),
    path('send_otp/', views.send_otp, name='send_otp'),
]

