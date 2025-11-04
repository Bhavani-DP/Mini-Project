from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('authenticate/', views.authenticate_voter, name='authenticate'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('submit_otp/', views.submit_otp, name='submit_otp'),
    path('vote/', views.vote_page, name='vote'),
    path('cast_vote/', views.cast_vote, name='cast_vote'),
    path('vote_success/', views.vote_success, name='vote_success'),
    path('vote_count/', views.vote_count, name='vote_count'),
    path('mine_block/', views.mine_block, name='mine_block'),
    path('blockchain/', views.blockchain_view, name='blockchain'),
]