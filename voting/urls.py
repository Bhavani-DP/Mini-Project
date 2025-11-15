from django.urls import path
from . import views

urlpatterns = [
    # Aadhaar and OTP flow
    path('', views.home, name='home'),
    path('otp_sending/', views.otp_sending, name='otp_sending'),
    path('confirm_otp/', views.confirm_otp, name='confirm_otp'),
    path('verify_email/', views.verify_email, name='verify_email'),
    #path('verify/', views.verify_aadhaar, name='verify_aadhaar'),
    path('aadhaar/', views.verify_aadhaar, name='verify_aadhaar'),
    path('change_email/', views.change_email, name='change_email'),
    
    # Voting flow
    path('cast_vote/', views.cast_vote, name='cast_vote'),
    path('submit_otp/', views.submit_vote, name='submit_otp'),
    path('vote/', views.vote, name='vote'),
    path('vote_success/', views.vote_success, name='vote_success'),
    path('confirm_vote/', views.confirm_vote, name='confirm_vote'),
    path('finalize_vote/', views.finalize_vote, name='finalize_vote'),

    # Blockchain and utility
    path('vote_count/', views.vote_count, name='vote_count'),
    path('mine_block/', views.mine_block, name='mine_block'),
    path('blockchain/', views.blockchain_view, name='blockchain'),
    path('otp-form/', views.otp_form, name='otp_form'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_sms_otp/', views.verify_sms_otp, name='verify_sms_otp'),
    path('aadhaar_form/', views.aadhaar_form, name='aadhaar_form'),
]