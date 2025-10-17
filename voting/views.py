from django.shortcuts import render, redirect
from .models import Voter, PoliticalParty, Vote
from .blockchain import Blockchain
from .utils import generate_otp, send_email
from django.contrib import messages
import hashlib, datetime

blockchain = Blockchain()
otp_store = {}  # Temporary in-memory store

def home(request):
    return render(request, 'home.html')

def authenticate_voter(request):
    if request.method == 'POST':
        aadhar = request.POST.get('aadhar')
        try:
            voter = Voter.objects.get(aadhar_number=aadhar)
            request.session['voter_id'] = voter.id
            return redirect('verify_email')
        except Voter.DoesNotExist:
            messages.error(request, 'Invalid Aadhar number')
    return render(request, 'authenticate.html')

def verify_email(request):
    voter = Voter.objects.get(id=request.session['voter_id'])
    otp = generate_otp()
    otp_store[voter.email] = otp
    send_email(voter.email, 'Your OTP for Voting', f'Your OTP is: {otp}')
    return render(request, 'verify_email.html', {'email': voter.email})

def submit_otp(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        voter = Voter.objects.get(id=request.session['voter_id'])
        if otp_store.get(voter.email) == otp_input:
            return redirect('vote')
        else:
            messages.error(request, 'Invalid OTP')
    return redirect('verify_email')

def vote_page(request):
    voter = Voter.objects.get(id=request.session['voter_id'])
    parties = PoliticalParty.objects.all()
    return render(request, 'vote.html', {'voter': voter, 'parties': parties})

def cast_vote(request):
    if request.method == 'POST':
        party_id = request.POST.get('party')
        voter = Voter.objects.get(id=request.session['voter_id'])
        party = PoliticalParty.objects.get(id=party_id)

        ballot_data = f'{voter.aadhar_number}-{party.name}-{datetime.datetime.now()}'
        ballot_hash = hashlib.sha256(ballot_data.encode()).hexdigest()
        signature = hashlib.sha256((ballot_hash + 'PRIVATE_KEY').encode()).hexdigest()

        Vote.objects.create(voter=voter, party=party, ballot_hash=ballot_hash, signature=signature)
        voter.vote_done = True
        voter.save()

        blockchain.add_vote({'voter': voter.aadhar_number, 'party': party.name, 'hash': ballot_hash})
        return redirect('vote_success')
    return redirect('vote')

def vote_success(request):
    voter = Voter.objects.get(id=request.session['voter_id'])
    vote = Vote.objects.filter(voter=voter).last()
    return render(request, 'vote_success.html', {'vote': vote})

def vote_count(request):
    parties = PoliticalParty.objects.all()
    counts = {party.name: Vote.objects.filter(party=party).count() for party in parties}
    return render(request, 'vote_count.html', {'counts': counts})

def mine_block(request):
    blockchain.mine()
    return redirect('blockchain')

def blockchain_view(request):
    return render(request, 'blockchain.html', {'chain': blockchain.chain})