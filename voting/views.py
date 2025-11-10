import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .models import Voter, PoliticalParty, Vote
from election.forms import OTPForm, UIDForm
from blockchain.utils import sign_vote
from django.urls import reverse
from django.http import JsonResponse
from django.http import HttpResponse
from twilio.rest import Client
from .twilio_utils import send_otp_sms
import datetime

def home(request):
    return render(request, "election/aadhaar_form.html")

from django.shortcuts import render

def verify_aadhaar(request):
    if request.method == "POST":
        aadhaar = request.POST.get("aadhaar", "").replace(" ", "")
        
        if not aadhaar.isdigit() or len(aadhaar) != 12:
            return render(request, "election/aadhaar_form.html", {
                "error": "Invalid Aadhaar number. Please enter a 12-digit number."
            })

        # Dummy voter data (replace with DB lookup later)
        voter_data = {
            "aadhaar": aadhaar,
            "name": "Madhan",
            "dob": "May 2, 1929",
            "epic": "600044",
            "state": "Tamil Nadu",
            "email": "xpertieee@gmail.com"  
        }

        return render(request, "election/voter_details.html", voter_data)
    
    return render(request, "election/aadhaar_form.html")

def verify_email(request):
    if request.method == 'POST':
        aadhaar = request.POST.get('aadhaar', '').strip()
        print("Submitted Aadhaar:", aadhaar)

        try:
            voter = Voter.objects.get(uid=aadhaar)
        except Voter.DoesNotExist:
            return render(request, 'voting/aadhaar_form.html', {'error': 'Invalid Aadhaar'})

        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        request.session['uid'] = aadhaar
        print("Generated OTP:", otp)

        # ✅ Send OTP to voter's email
        send_mail(
            subject='Your OTP for Online Voting',
            message=f'Your OTP is: {otp}',
            from_email='your_email@gmail.com',
            recipient_list=[voter.email],
            fail_silently=False,
        )
        print("Redirecting to confirm_otp")
        return redirect('http://127.0.0.1:8000/confirm_otp/')
    return render(request, 'home.html')

def confirm_otp(request):
    print("✅ confirm_otp view reached")

    if request.session.get('email_verified'):
        return redirect('cast_vote')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            stored_otp = request.session.get('otp')

            if entered_otp == stored_otp:
                request.session['email_verified'] = True
                aadhaar = request.session.get('uid')
                voter = Voter.objects.get(uid=aadhaar)
                request.session['voter_id'] = voter.id
                return redirect('cast_vote')
            else:
                form.add_error('otp', 'Invalid OTP')
    else:
        form = OTPForm()

    return render(request, 'election/verify_email_otp.html', {'form': form})

def cast_vote(request):
    voter_id = request.session.get('voter_id')
    if not voter_id:
        return redirect('verify_email')

    try:
        voter = Voter.objects.get(id=voter_id)
    except Voter.DoesNotExist:
        return redirect('verify_email')

    parties = PoliticalParty.objects.all()
    email_verified = request.session.get('email_verified', False)

    return render(request, 'election/cast_vote.html', {
        'voter': voter,
        'parties': parties,
        'email_verified': email_verified
    })

def vote(request):
    return HttpResponse("Vote page placeholder")

def submit_vote(request):
    voter_id = request.session.get('voter_id')
    if not voter_id:
        return redirect('verify_email')

    voter = Voter.objects.get(id=voter_id)
    latest_vote = Vote.objects.filter(voter=voter).last()

    return render(request, 'election/vote_success.html', {
        'voter': voter,
        'ballot_hash': latest_vote.hash,
        'signature': latest_vote.signature
    })

def confirm_vote(request):
    if request.method == 'POST':
        party_id = request.POST.get('party')
        try:
            party = PoliticalParty.objects.get(id=party_id)
            return render(request, 'election/confirm_vote.html', {'party': party})
        except PoliticalParty.DoesNotExist:
            return redirect('cast_vote')
    return redirect('cast_vote')

def finalize_vote(request):
    if request.method == 'POST':
        voter_id = request.session.get('voter_id')
        party_id = request.POST.get('party_id')
        private_key = request.POST.get('private_key')

        voter = Voter.objects.get(id=voter_id)
        party = PoliticalParty.objects.get(id=party_id)

        timestamp = datetime.datetime.now().isoformat()
        ballot_hash, gov_signature = sign_vote(voter.uid, party.party_id, timestamp, secret=private_key)

        Vote.objects.create(
            voter=voter,
            party=party,
            vote_time=timestamp,
            hash=ballot_hash,
            previous_hash='prev_hash_placeholder',
            signature=gov_signature
        )
        voter.vote_done = True
        voter.save()

        return render(request, 'election/vote_signed.html', {
            'voter': voter,
            'ballot_hash': ballot_hash,
            'gov_signature': gov_signature
        })
    return redirect('cast_vote')

def vote_success(request):
    return HttpResponse("Your vote was successfully recorded.")

def vote_count(request):
    return HttpResponse("Vote count page placeholder")

def otp_form(request):
    return render(request, 'otp_form.html')

def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone')  # e.g. 968698XXXX
        to_number = '+91' + phone_number.strip()  # ✅ Add country code

        account_sid = 'AC7bae80ba2d7ec137e84e71123be96eef'
        auth_token = 'a18a47253718e82de72c6ddb4ab5fcbf'
        client = Client(account_sid, auth_token)

        otp = str(random.randint(100000, 999999))  # ✅ Generate OTP
        body = f"Your OTP is {otp}"

        try:
            message = client.messages.create(
                body=body,
                from_='+12173876498',  # ✅ Your Twilio number
                to=to_number
            )
            return HttpResponse("OTP sent successfully.")
        except Exception as e:
            return HttpResponse(f"Twilio error: {str(e)}")
    email = request.POST.get('email')
    otp = str(random.randint(100000, 999999))

    # Store OTP in session
    request.session['otp'] = otp
    request.session['email'] = email

    send_mail(
        subject='Your Voting OTP',
        message=f'Your OTP is: {otp}',
        from_email='yourgmail@gmail.com',
        recipient_list=[email],
        fail_silently=False,
    )

    return render(request, 'election/enter_otp.html', {'email': email})
    
def submit_otp(request):
    return HttpResponse("OTP submitted successfully.")

def mine_block(request):
    return HttpResponse("Block mined successfully.")

def blockchain_view(request):
    return HttpResponse("Blockchain view placeholder")

def verify_sms_otp(request):
    return HttpResponse("SMS OTP verified.")


