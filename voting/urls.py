from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Landing & navigation
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),

    # Biometric & Aadhaar verification
    path('biometric/', views.biometric_page, name='biometric_page'),
    path('verify-aadhaar/', views.verify_aadhaar, name='verify_aadhaar'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('aadhaar_form/', views.aadhaar_form, name='aadhaar_form'),
    path('voter/details/', views.voter_details, name='voter_details'),
    path("verify-face/<int:voter_id>/", views.verify_face, name="verify_face"),

    # Email & OTP flows
    path('verify-email/', views.verify_email, name='verify_email'),
    path('otp-sending/', views.otp_sending, name='otp_sending'),
    path('verify_email_otp/', views.verify_email_otp, name='verify_email_otp'),
    path('change_email/', views.change_email, name='change_email'),
    path('confirm_otp/', views.confirm_otp, name='confirm_otp'),
    path('otp-form/', views.otp_form, name='otp_form'),
    path("change_phone/", views.change_phone_number, name="change_phone"),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_sms_otp/', views.verify_sms_otp, name='verify_sms_otp'),
    path('submit_otp/', views.submit_vote, name='submit_otp'),

    # Voting flows
    path('vote/', views.vote, name='vote'),
    path('cast_vote/', views.cast_vote, name='cast_vote'),
    path('select-party/', views.select_party, name='select_party'),
    path('vote_success/', views.vote_success, name='vote_success'),
    path('confirm_vote/', views.confirm_vote, name='confirm_vote'),
    path('finalize_vote/', views.finalize_vote, name='finalize_vote'),
    path('vote_count/', views.vote_count, name='vote_count'),

    # Voter management
    path("add-voter/", views.add_voter, name="add_voter"),

    # Blockchain
    path('mine_block/', views.mine_block, name='mine_block'),
    path('blockchain/', views.blockchain_view, name='blockchain'),
    
    # WebAuthn flows
    path('webauthn/register/start/', views.webauthn_register_start, name='webauthn_register_start'),
    path('webauthn/register/finish/', views.webauthn_register_finish, name='webauthn_register_finish'),
    path('webauthn/auth/start/', views.webauthn_auth_start, name='webauthn_auth_start'),
    path('webauthn/auth/finish/', views.webauthn_auth_finish, name='webauthn_auth_finish'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)