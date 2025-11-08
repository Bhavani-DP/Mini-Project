from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('authenticate/', views.verify_email, name='authenticate'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('submit_otp/', views.submit_vote, name='submit_otp'),
    path('vote/', views.vote, name='vote'),
    path('cast_vote/', views.cast_vote, name='cast_vote'),
    path('vote_success/', views.vote_success, name='vote_success'),
    path('vote_count/', views.vote_count, name='vote_count'),
    path('mine_block/', views.mine_block, name='mine_block'),
    path('blockchain/', views.blockchain_view, name='blockchain'),
    path('otp-form/', views.otp_form, name='otp_form'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('aadhaar/', views.verify_aadhaar, name='verify_aadhaar'), 
]