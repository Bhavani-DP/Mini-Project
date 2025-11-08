from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .models import Voter, PoliticalParty, Vote
import random

# 🔹 Admin-style login view
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/admin/')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

# 🔹 Aadhaar authentication view
def aadhaar_auth(request):
    if request.method == 'POST':
        uid = request.POST.get('aadhaar')
        try:
            voter = Voter.objects.get(uid=uid)
            request.session['voter_id'] = voter.id
            return redirect('voter_details')
        except Voter.DoesNotExist:
            return render(request, 'election/aadhaar_auth.html', {'error': 'Invalid Aadhaar Number'})
    return render(request, 'election/aadhaar_auth.html')

# 🔹 Voter details page
def voter_details(request):
    voter_id = request.session.get('voter_id')
    if not voter_id:
        return redirect('aadhaar_auth')
    voter = Voter.objects.get(id=voter_id)
    return render(request, 'election/voter_details.html', {'voter': voter})

# 🔹 Email verification page
def verify_email(request):
    voter_id = request.session.get('voter_id')
    if not voter_id:
        return redirect('aadhaar_auth')
    voter = Voter.objects.get(id=voter_id)
    if request.method == 'POST':
        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        send_mail(
            'Your Voting OTP',
            f'Your OTP is: {otp}',
            'noreply@election.com',
            [voter.email],
            fail_silently=False,
        )
        return redirect('confirm_otp')
    return render(request, 'election/verify_email.html', {'voter': voter})

# 🔹 OTP confirmation page
def confirm_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == request.session.get('otp'):
            request.session['email_verified'] = True
            return redirect('cast_vote')
        else:
            return render(request, 'election/confirm_otp.html', {'error': 'Invalid OTP'})
    return render(request, 'election/confirm_otp.html')

# 🔹 Vote casting page
def cast_vote(request):
    voter_id = request.session.get('voter_id')
    if not voter_id:
        return redirect('aadhaar_auth')
    voter = Voter.objects.get(id=voter_id)
    parties = PoliticalParty.objects.all()
    email_verified = request.session.get('email_verified', False)
    return render(request, 'election/cast_vote.html', {
        'voter': voter,
        'parties': parties,
        'email_verified': email_verified
    })

# 🔹 Vote submission
def submit_vote(request):
    if request.method == 'POST':
        voter_id = request.session.get('voter_id')
        party_id = request.POST.get('party')
        voter = Voter.objects.get(id=voter_id)
        party = PoliticalParty.objects.get(id=party_id)
        Vote.objects.create(
            voter=voter,
            party=party,
            vote_time='Now',
            hash='dummy_hash',
            previous_hash='dummy_prev',
            signature='dummy_signature'
        )
        voter.vote_done = True
        voter.save()
        return render(request, 'election/thank_you.html')
    return redirect('cast_vote')
# 🔹 Confirm selected party and enter private key
def confirm_vote(request):
    if request.method == 'POST':
        party_id = request.POST.get('party')
        party = PoliticalParty.objects.get(id=party_id)
        return render(request, 'election/confirm_vote.html', {'party': party})

# 🔹 Finalize vote and show signed result
def finalize_vote(request):
    if request.method == 'POST':
        voter_id = request.session.get('voter_id')
        party_id = request.POST.get('party_id')
        private_key = request.POST.get('private_key')

        voter = Voter.objects.get(id=voter_id)
        party = PoliticalParty.objects.get(id=party_id)

        # Simulated hash and signature
        ballot_hash = '4cf13b4400c4e4f44d99655c20e6d238527d6e609f9f87c208b2f7f7056555'
        gov_signature = '6a0c3e3e5c2a7b7a7abbdc4222489b3b' + 'e4' * 100

        Vote.objects.create(
            voter=voter,
            party=party,
            vote_time='Now',
            hash=ballot_hash,
            previous_hash='prev_hash',
            signature=gov_signature
        )
        voter.vote_done = True
        voter.save()

        return render(request, 'election/vote_signed.html', {
            'voter': voter,
            'ballot_hash': ballot_hash,
            'gov_signature': gov_signature
        })

    