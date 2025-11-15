import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import Voter, PoliticalParty, Vote
from election.forms import OTPForm, UIDForm
from blockchain.utils import sign_vote
from django.urls import reverse
from django.http import JsonResponse
from django.http import HttpResponse
from twilio.rest import Client
from .twilio_utils import send_otp_sms
import datetime
from .models import Voter
from election.forms import OTPForm 

def home(request):
    return render(request, "election/aadhaar_form.html")

def verify_aadhaar(request):
    if request.method == "POST":
        aadhaar = request.POST.get("aadhaar", "").replace(" ", "")

        if not aadhaar.isdigit() or len(aadhaar) != 12:
            return render(request, "election/aadhaar_form.html", {
                "error": "Invalid Aadhaar number. Please enter a 12-digit number."
            })

        try:
            voter = Voter.objects.get(aadhar_number=aadhaar)
        except Voter.DoesNotExist:
            return render(request, "election/aadhaar_form.html", {
                "error": "No voter found with this Aadhaar number."
            })

        request.session['aadhar_number'] = aadhaar
        request.session.modified = True

        form = OTPForm()
        return render(request, 'election/voter_details.html', {
            'voter': voter,
            'form': form
        })

    # ✅ Handle GET request after waiting page
    aadhaar = request.session.get('aadhar_number')
    if aadhaar:
        try:
            voter = Voter.objects.get(aadhar_number=aadhaar)
            form = OTPForm()
            return render(request, 'election/voter_details.html', {
                'voter': voter,
                'form': form
            })
        except Voter.DoesNotExist:
            messages.error(request, "Session Aadhaar not found in database.")
            return redirect('verify_email')

    # ❌ No session — show input form
    return render(request, "election/aadhaar_form.html")

def verify_email(request):
    if request.method == 'POST':
        aadhaar = request.POST.get('aadhaar', '').strip()

        try:
            voter = Voter.objects.get(aadhar_number=aadhaar)
        except Voter.DoesNotExist:
            return render(request, 'election/aadhaar_form.html', {'error': 'Invalid Aadhaar'})

        otp = str(random.randint(100000, 999999))
        aadhaar = request.session.get('aadhar_number')
        request.session['otp'] = otp
        print("Session Aadhaar:", request.session.get('aadhar_number'))

        send_mail(
            subject='Your OTP for Online Voting',
            message=f'Your OTP is: {otp}',
            from_email='your_email@gmail.com',
            recipient_list=[voter.email],
            fail_silently=False,
        )

        messages.success(request, "Enter the OTP sent to your email.")

        # ✅ Ensure session is saved before redirect
        request.session.modified = True
        return redirect('otp_sending')

    return redirect('home') 

def otp_sending(request):
    return render(request, 'election/otp_sending.html')

def confirm_otp(request):
    aadhaar = request.session.get('aadhar_number')
    if not aadhaar:
        messages.error(request, "Session expired. Please re-enter your Aadhaar number.")
        return redirect('verify_aadhaar')

    try:
        voter = Voter.objects.get(aadhar_number=aadhaar)
    except Voter.DoesNotExist:
        return redirect('home')

    form = OTPForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            session_otp = request.session.get('otp')

            if entered_otp == session_otp:
                messages.success(request, "OTP verified successfully.")
                return render(request, 'election/verify_email_otp.html', {
                    'form': OTPForm(),  # fresh form
                    'voter': voter
                })
            else:
                messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'election/verify_email_otp.html', {
        'form': form,
        'voter': voter
    })

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
        ballot_hash, gov_signature = sign_vote(voter.aadhar_number, party.party_id, timestamp, secret=private_key)

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
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        otp = str(random.randint(100000, 999999))

        if email:
            send_mail(
                'Your OTP',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

        if phone_number:
            to_number = '+91' + phone_number.strip()
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f'Your OTP is: {otp}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )

        return render(request, 'election/otp_sending.html')  
    
def submit_otp(request):
    return HttpResponse("OTP submitted successfully.")

def mine_block(request):
    return HttpResponse("Block mined successfully.")

def blockchain_view(request):
    return HttpResponse("Blockchain view placeholder")

def verify_sms_otp(request):
    return HttpResponse("SMS OTP verified.")

def change_email(request):
    return render(request, 'election/change_email.html')  

def verify_email_otp(request):
    aadhaar = request.session.get('aadhar_number')

    if not aadhaar:
        return redirect('home') 

    try:
        voter = Voter.objects.get(aadhar_number=aadhaar)
    except Voter.DoesNotExist:
        return redirect('home')  

    form = OTPForm()

    return render(request, 'election/verify_email_otp.html', {
        'form': form,
        'voter': voter
    })

def aadhaar_form(request):
    return render(request, 'election/aadhaar_form.html')






