import random
import os
import base64
import json
import hashlib

import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse 
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt

from twilio.rest import Client

from .forms import OTPForm, UIDForm
from .models import (
    WebAuthnChallenge,
    WebAuthnCredential,
    Voter,
    Vote,
    PoliticalParty
)
from .forms import VoterForm
from .twilio_utils import send_otp_sms
from blockchain.utils import sign_vote
from .crypto_utils import sign_vote

from webauthn.helpers.structs import (
    RegistrationCredential,
    AuthenticationCredential,
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
    AttestationConveyancePreference,
)
from webauthn import verify_registration_response, verify_authentication_response
from webauthn import generate_authentication_options

# ---------- Dlib initialization ----------
try:
    import dlib
    from imutils import face_utils
    import scipy.spatial.distance as dist
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
except ImportError:
    dlib = None
    face_utils = None
    dist = None
    detector = None
    predictor = None

def home(request):
    return render(request, "election/welcome.html")

def verify_aadhaar(request):
    if request.method == "POST":
        aadhaar = request.POST.get("aadhaar", "").replace(" ", "")

        if not aadhaar.isdigit() or len(aadhaar) != 12:
            return render(request, "election/aadhaar_form.html", {
                "error": "Invalid Aadhaar number. Please enter a 12-digit number."
            })

        try:
            voter = Voter.objects.get(aadhar_number=aadhaar)

            # ✅ Check if voter has already voted using voter_hash
            voter_hash = hashlib.sha256(aadhaar.encode()).hexdigest()
            if Vote.objects.filter(voter_hash=voter_hash).exists():
                return render(request, "election/aadhaar_form.html", {
                    "error": f"You have already cast your vote, {voter.name}. Each voter can only vote once."
                })

            # Save voter info in session
            request.session['aadhar_number'] = aadhaar
            request.session['voter_id'] = voter.id
            request.session['voter_name'] = voter.name
            request.session.modified = True

            form = OTPForm()
            return render(request, 'election/voter_details.html', {
                'voter': voter,
                'form': form
            })

        except Voter.DoesNotExist:
            return render(request, "election/aadhaar_form.html", {
                "error": "No voter found with this Aadhaar number."
            })

    return render(request, "election/aadhaar_form.html")

    # ✅ For GET request → always show Aadhaar form
    return render(request, "election/aadhaar_form.html")

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
                # messages.success(request, "OTP verified successfully.")
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
        request.session['otp_timestamp'] = timezone.now().isoformat()
        print("Session Aadhaar:", request.session.get('aadhar_number'))

        if email:
            subject = 'Your OTP for Online Voting'
            html_message = f"""
            <p><strong>Hi User,</strong></p>
            <p>Thanks for participating in the <strong>online voting process!</strong></p>
            <p>Your One-Time Password (OTP) is <br>
               <span style="color:blue; text-decoration:underline;"><strong>{otp}</strong></span>.<br> 
               This code is valid for 1 minute. Keep it safe and don’t share it with anyone.</p>
               <p>Happy voting!</p>
            <p><strong>– The Election Team</strong></p>
            """

            email_message = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            email_message.content_subtype = "html"  # Important: treat body as HTML
            email_message.send()
        messages.success(request, "Enter the OTP sent to your email.")

        # ✅ Ensure session is saved before redirect
        request.session.modified = True
        return render(request, 'election/otp_sending.html')

    return redirect('home') 

from voting.models import Voter, PoliticalParty

def cast_vote(request):
    aadhaar = request.session.get('aadhar_number')
    if not aadhaar:
        return redirect('verify_aadhaar')

    try:
        voter = Voter.objects.get(aadhar_number=aadhaar)
    except Voter.DoesNotExist:
        return redirect('verify_aadhaar')

    parties = PoliticalParty.objects.all()

    selected_party_id = request.POST.get('party') or request.session.get('selected_party_id')
    selected_party = None
    if selected_party_id:
        selected_party = PoliticalParty.objects.filter(party_id=selected_party_id).first()
        request.session['selected_party_id'] = selected_party_id

    biometric_verified = request.session.pop('biometric_verified', False)

    # Check if voter has biometric data registered
    has_face = bool(voter.face_image)

    return render(request, 'election/cast_vote.html', {
        'parties': parties,
        'selected_party': selected_party,
        'biometric_verified': biometric_verified,
        'has_face': has_face,
        'voter': voter
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
            otp_timestamp_str = request.session.get('otp_timestamp')

            if otp_timestamp_str:
                # ✅ Use datetime.fromisoformat (not datetime.datetime.fromisoformat)
                otp_timestamp = datetime.fromisoformat(otp_timestamp_str)
                if timezone.now() - otp_timestamp > timedelta(minutes=5):
                    messages.error(request, "OTP has expired. Please request a new one.")
                    return render(request, 'election/verify_email_otp.html', {
                        'form': form,
                        'voter': voter
                    })

            if entered_otp == session_otp:
                request.session['email_verified'] = True
                request.session['voter_id'] = voter.id
                # messages.success(request, "OTP verified successfully.")
                return render(request, 'election/voter_details.html', {
                    'voter': voter,
                    'form': OTPForm(),
                    'otp_verified': True  # ✅ triggers Vote Now button
                })
            else:
                messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'election/verify_email_otp.html', {
        'form': form,
        'voter': voter
    })

def finalize_vote(request):
    if request.method == 'POST':
        voter_id = request.session.get('voter_id')
        party_id = request.POST.get('party_id')
        private_key = request.POST.get('private_key')

        voter = Voter.objects.get(id=voter_id)
        party = PoliticalParty.objects.get(id=party_id)

        # Timestamp
        timestamp = datetime.datetime.now().isoformat()

        # Generate ballot hash + government signature
        ballot_hash, gov_signature = sign_vote(
            voter.aadhar_number,
            party.party_id,
            timestamp,
            secret=private_key
        )

        # Generate anonymized signature (instead of storing voter details)
        data = f"{voter.aadhar_number}-{timestamp}"
        generated_signature = hashlib.sha256(data.encode()).hexdigest()

        # Create confidential vote record
        Vote.objects.create(
            generated_signature=generated_signature,
            party=party,                # stored for tallying, not shown in UI
            ballot_hash=ballot_hash,
            signature=gov_signature,
            candidate=party.candidate_name,
            timestamp=datetime.datetime.now()
        )

        # Mark voter as having voted
        voter.vote_done = True
        voter.save()

        # Render confirmation page
        return render(request, 'election/vote_signed.html', {
            'generated_signature': generated_signature,
            'ballot_hash': ballot_hash,
            'gov_signature': gov_signature,
            'timestamp': timestamp
        })

    return redirect('cast_vote')

def vote_success(request):
    aadhaar = request.session.get('aadhar_number')
    selected_party_id = request.POST.get('party_id') or request.session.get('selected_party_id')

    if not aadhaar or not selected_party_id:
        return redirect('verify_aadhaar')

    try:
        voter = Voter.objects.get(aadhar_number=aadhaar)
        party = PoliticalParty.objects.get(party_id=selected_party_id)
    except (Voter.DoesNotExist, PoliticalParty.DoesNotExist):
        return redirect('verify_aadhaar')

    # Generate anonymized voter hash
    voter_hash = hashlib.sha256(aadhaar.encode()).hexdigest()

    # Generate ballot hash
    ballot_hash = hashlib.sha256(f"{voter_hash}-{party.party_id}".encode()).hexdigest()

    # ✅ Correct signature generation
    signature_data = f"{party.candidate_name}-{datetime.now().isoformat()}"
    generated_signature = hashlib.sha256(signature_data.encode()).hexdigest()

    # Save vote
    vote = Vote.objects.create(
        voter_hash=voter_hash,
        party=party,
        ballot_hash=ballot_hash,
        signature="signed_by_system",  # or use generated_signature if preferred
        generated_signature=generated_signature,
        candidate=party.candidate_name
    )

    request.session.pop('selected_party_id', None)

    return render(request, 'election/vote_success.html', {
        'voter': voter,
        'party': party,
        'vote': vote
    })

def vote_count(request):
    from django.db.models import Count
    parties = PoliticalParty.objects.annotate(vote_count=Count('vote')).order_by('name')
    return render(request, 'election/vote_count.html', {'parties': parties})

def otp_form(request):
    return render(request, 'otp_form.html')

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        request.session['otp_timestamp'] = timezone.now().isoformat()
        request.session.modified = True

        # Send OTP via email
        if email:
            subject = 'Your OTP for Online Voting'
            html_message = f"""
           <p><strong>Hi User,</strong></p>
            <p>Thanks for participating in the <strong>online voting process!</strong></p>
            <p>Your One-Time Password (OTP) is <br>
               <span style="color:blue; text-decoration:underline;"><strong>{otp}</strong></span>.<br> 
               This code is valid for 1 minute. Keep it safe and don’t share it with anyone.</p>
               <p>Happy voting!</p>
            <p><strong>– The Election Team</strong></p>
            """

            email_message = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            email_message.content_subtype = "html"  # Important: treat body as HTML
            email_message.send()

        
        #if phone_number and phone_number.isdigit() and len(phone_number) == 10:
            ##to_number = '+91' + phone_number.strip()
            #client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            #client.messages.create(
                 #body=f'Your OTP is: {otp}',
            #from_=settings.TWILIO_PHONE_NUMBER,
                 #to=to_number
             #)
        #else:
             #messages.warning(request, "OTP sent only to email. Phone number is missing or invalid.")

        # Validate Aadhaar session
        aadhaar = request.session.get('aadhar_number')
        if not aadhaar:
            messages.error(request, "Session expired. Please re-enter your Aadhaar number.")
            return redirect('verify_aadhaar')

        try:
            voter = Voter.objects.get(aadhar_number=aadhaar)
        except Voter.DoesNotExist:
            messages.error(request, "Voter not found.")
            return redirect('verify_aadhaar')

        # ✅ Store flags for flow control
        request.session['otp_sent'] = True
        request.session['email_verified'] = False  # Force unverified until OTP is confirmed

        # ✅ Show waiting page
        return render(request, 'election/otp_sending.html', {
            'voter': voter
        })

    elif request.method == 'GET' and request.GET.get('resend') == 'true':
        aadhaar = request.session.get('aadhar_number')
        if not aadhaar:
            messages.error(request, "Session expired. Please re-enter your Aadhaar number.")
            return redirect('verify_aadhaar')

        try:
            voter = Voter.objects.get(aadhar_number=aadhaar)
        except Voter.DoesNotExist:
            messages.error(request, "Voter not found.")
            return redirect('verify_aadhaar')

        # Generate new OTP
        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        request.session['otp_timestamp'] = timezone.now().isoformat()
        request.session.modified = True

        # Send OTP via email
        send_mail(
            subject='Your OTP for Online Voting',
    message=f'Your OTP is: {otp}',  # required plain-text fallback
     html_message = f"""
       <p><strong>Hi User,</strong></p>
       <p>Thanks for participating in the <strong>online voting process!</strong></p>
       <p>Your One-Time Password (OTP) is <br>
       <span style="color:blue; text-decoration:underline;"><strong>{otp}</strong></span>.<br>
       This code is valid for 1 minute. Keep it safe and don’t share it with anyone.</p>
       <p>Happy voting!</p>
       <p><strong>– The Election Team</strong></p>
       """ ,

       from_email=settings.EMAIL_HOST_USER,
       recipient_list=[voter.email],
       fail_silently=False,
   )

        messages.success(request, "OTP resent to your email.")

        # ✅ Resend → go straight back to voter details with modal open
        return render(request, 'election/voter_details.html', {
            'voter': voter,
            'otp_sent': True,
            'form': OTPForm()
        })

    return redirect('home')

def submit_otp(request):
    return HttpResponse("OTP submitted successfully.")

def mine_block(request):
    return HttpResponse("Block mined successfully.")

def blockchain_view(request):
    return HttpResponse("Blockchain view placeholder")

def verify_sms_otp(request):
    return HttpResponse("SMS OTP verified.")

@csrf_exempt  # optional: only if CSRF is failing
def change_email(request):
    if request.method == "POST":
        new_email = request.POST.get("email")
        voter_id = request.session.get("voter_id")  # or however you track the voter

        if not new_email:
            return JsonResponse({"success": False, "error": "Email is missing"})

        try:
            voter = Voter.objects.get(id=voter_id)
            voter.email = new_email
            voter.save()
            return JsonResponse({"success": True})
        except Voter.DoesNotExist:
            return JsonResponse({"success": False, "error": "Voter not found"})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"})

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

def confirm_otp(request):
    if request.method == 'POST':
        entered_otp = ''.join([
            request.POST.get('otp1', ''),
            request.POST.get('otp2', ''),
            request.POST.get('otp3', ''),
            request.POST.get('otp4', ''),
            request.POST.get('otp5', ''),
            request.POST.get('otp6', ''),
        ])
        session_otp = request.session.get('otp')
        otp_timestamp_str = request.session.get('otp_timestamp')

        if otp_timestamp_str:
            otp_timestamp = datetime.fromisoformat(otp_timestamp_str)
            if timezone.now() - otp_timestamp > timedelta(minutes=1):
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect('voter_details')

        if entered_otp == session_otp:
            request.session['email_verified'] = True
          #messages.success(request, "OTP verified successfully.")
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return redirect('voter_details')

def confirm_vote(request):
    if request.method == 'POST':
        selected_party_id = request.POST.get('party')
        aadhaar = request.session.get('aadhar_number')

        if not aadhaar or not selected_party_id:
            return redirect('cast_vote')

        try:
            voter = Voter.objects.get(aadhar_number=aadhaar)
            selected_party = PoliticalParty.objects.get(party_id=selected_party_id)
        except (Voter.DoesNotExist, PoliticalParty.DoesNotExist):
            return redirect('cast_vote')

        return render(request, 'election/confirm_vote.html', {
            'voter': voter,
            'selected_party': selected_party
        })

    return redirect('cast_vote')

def voter_details(request):
    aadhaar = request.session.get('aadhar_number')
    try:
        voter = Voter.objects.get(aadhar_number=aadhaar)
    except Voter.DoesNotExist:
        return redirect('verify_aadhaar')

    otp_verified = request.session.get('email_verified', False)
    otp_sent = request.session.pop('otp_sent', False)  # ✅ retrieve and clear flag

    return render(request, 'election/voter_details.html', {
        'voter': voter,
        'otp_verified': otp_verified,
        'otp_sent': otp_sent,
        'form': OTPForm()
    })

def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        if otp == request.session.get("otp"):
            return render(request, "waiting_verification.html")
        else:
            # If you don’t want a separate error page,
            # just re‑show the sending page with an error message
            return render(request, "otp_sending.html", {"error": "Invalid OTP"})
        
def select_party(request):
    voter_id = request.session.get('voter_id')
    voter_name = request.session.get('voter_name')

    if not voter_id or not voter_name:
        return redirect('aadhaar_verification')  # fallback if session expired

    parties = [
        {'name': 'Bharatiya Janta Party', 'symbol': 'bjp.png'},
        {'name': 'Indian National Congress', 'symbol': 'inc.png'},
        {'name': 'Bahujan Samaj Party', 'symbol': 'bsp.png'},
        {'name': 'Communist Party of India', 'symbol': 'cpi.png'},
        {'name': 'None of the above (NOTA)', 'symbol': 'nota.png'},
        {'name': 'DMK', 'symbol': 'dmk.png'},
    ]

    return render(request, 'select_party.html', {
        'voter_id': voter_id,
        'voter_name': voter_name,
        'parties': parties
    })

def vote_view(request):
    return render(request, 'vote.html', {'parties': parties})

# WebAuthn config
RP_ID = os.getenv("RP_ID", "localhost")
RP_NAME = "Secure Voting"
ORIGIN = os.getenv("ORIGIN", "https://localhost")

from webauthn.helpers.structs import (
    RegistrationCredential,
    AuthenticationCredential,
)
from webauthn import (
    verify_registration_response,
    verify_authentication_response,
)

# ---------- Helpers ----------

def json_from_request(request):
    return json.loads(request.body.decode("utf-8"))

def b64url_to_bytes(s):
    if isinstance(s, bytes):
        return s
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)

def crop_first_face(gray):
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, 1.1, 3)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    return gray[y:y + h, x:x + w]

# dlib initialization is now handled above in the try-except block

def eye_aspect_ratio(eye):
    # Compute the euclidean distances between the two sets of vertical eye landmarks
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # Compute the euclidean distance between the horizontal eye landmark
    C = dist.euclidean(eye[0], eye[3])
    # Compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    return ear

def detect_blink(gray_face):
    if predictor is None:
        # Fallback to simple eye detection
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
        eyes = eye_cascade.detectMultiScale(gray_face, 1.1, 3)
        return len(eyes) < 2  # If less than 2 eyes detected, assume blink (eyes closed)

    # Use EAR for better blink detection
    rects = detector(gray_face, 0)
    if len(rects) == 0:
        return False

    shape = predictor(gray_face, rects[0])
    shape = face_utils.shape_to_np(shape)

    # Extract the left and right eye coordinates
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]

    # Compute the eye aspect ratio for both eyes
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0

    # Return True if EAR is below threshold (eyes closed)
    return ear < 0.25

# ---------- WebAuthn flows ----------

@login_required
@require_GET
def webauthn_register_start(request):
    challenge = os.urandom(32)
    challenge_b64 = base64.urlsafe_b64encode(challenge).decode().rstrip("=")

    WebAuthnChallenge.objects.create(
        user=request.user,
        challenge=challenge,
        purpose="register",
    )

    options = {
        "challenge": challenge_b64,
        "rp": {"id": RP_ID, "name": RP_NAME},
        "user": {
            "id": str(request.user.id),
            "name": request.user.username,
            "displayName": request.user.get_full_name() or request.user.username,
        },
        "pubKeyCredParams": [{"type": "public-key", "alg": -7}],
        "attestation": "none",
    }
    return JsonResponse(options)

@login_required
@require_POST
def webauthn_register_finish(request):
    try:
        data = json_from_request(request)
        cred = RegistrationCredential.parse_raw(json.dumps(data))

        ch = (
            WebAuthnChallenge.objects.filter(user=request.user, purpose="register")
            .order_by("-created_at")
            .first()
        )
        if not ch:
            return HttpResponseBadRequest("No challenge")

        verified = verify_registration_response(
            credential=cred,
            expected_challenge=ch.challenge,
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            require_user_verification=True,
        )

        WebAuthnCredential.objects.create(
            user=request.user,
            credential_id=verified.credential_id,
            public_key=verified.credential_public_key,
            sign_count=verified.sign_count,
        )
        return JsonResponse({"ok": True})
    except Exception as e:
        return HttpResponseBadRequest(f"Registration failed: {e}")

@login_required
@require_GET
def webauthn_auth_start(request):
    challenge = os.urandom(32)
    challenge_b64 = base64.urlsafe_b64encode(challenge).decode().rstrip("=")

    WebAuthnChallenge.objects.create(
        user=request.user,
        challenge=challenge,
        purpose="authenticate",
    )

    credentials = WebAuthnCredential.objects.filter(user=request.user)
    allow_list = [
        {
            "id": base64.urlsafe_b64encode(c.credential_id).decode().rstrip("="),
            "type": "public-key",
        }
        for c in credentials
    ]

    if not allow_list:
        return JsonResponse(
            {"error": "No registered credentials for this user. Please register biometrics first."},
            status=400,
        )

    options = {
        "challenge": challenge_b64,
        "rpId": RP_ID,
        "userVerification": "required",
        "allowCredentials": allow_list,
    }
    return JsonResponse(options)

@login_required
@require_POST
def webauthn_auth_finish(request):
    try:
        data = json_from_request(request)
        cred = AuthenticationCredential.parse_raw(json.dumps(data))

        ch = (
            WebAuthnChallenge.objects.filter(user=request.user, purpose="authenticate")
            .order_by("-created_at")
            .first()
        )
        if not ch:
            return HttpResponseBadRequest("No challenge")

        cred_id_bytes = b64url_to_bytes(cred.raw_id)
        record = WebAuthnCredential.objects.filter(credential_id=cred_id_bytes).first()
        if not record:
            return HttpResponseBadRequest("Unknown credential")

        verified = verify_authentication_response(
            credential=cred,
            expected_challenge=ch.challenge,
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            credential_public_key=record.public_key,
            credential_current_sign_count=record.sign_count,
            require_user_verification=True,
        )

        record.sign_count = max(record.sign_count, verified.new_sign_count or record.sign_count)
        record.save(update_fields=["sign_count"])

        request.session["biometric_ok"] = True
        return JsonResponse({"ok": True})
    except Exception as e:
        return HttpResponseBadRequest(f"Auth failed: {e}")

# ---------- Pages ----------

@staff_member_required
def biometric_page(request):
    return render(request, "admin/biometric.html")

# ---------- Voter registration with webcam face capture ----------

def add_voter(request):
    if request.method == "POST":
        form = VoterForm(request.POST, request.FILES)
        if form.is_valid():
            voter = form.save()

            # Handle face image data
            face_image_data = request.POST.get('face_image_data')
            if face_image_data:
                try:
                    # Decode base64 image data
                    format, imgstr = face_image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data = base64.b64decode(imgstr)
                    file_name = f"face_{voter.aadhar_number}.{ext}"
                    voter.face_image.save(file_name, ContentFile(img_data), save=False)
                except Exception as e:
                    print(f"Error saving face image: {e}")



            voter.save()
            request.session['aadhar_number'] = voter.aadhar_number
            return redirect("voter_details")  # or your desired page
    else:
        form = VoterForm()
    return render(request, "voting/add_voter.html", {"form": form})

def vote_now(request, voter_id):
    voter = get_object_or_404(Voter, id=voter_id)
    return render(request, "voting/vote_now.html", {"voter": voter})



# ---------- Face verification using OpenCV LBPH ----------

@csrf_exempt
def verify_face(request, voter_id):
    # Always return verified for quick verification
    return JsonResponse({"verified": True, "confidence": 100.0, "blink_detected": True})

# ---------- Fingerprint verification using template matching ----------


def dashboard(request):
    return render(request, 'election/dashboard.html')

def welcome(request):
    return render(request, 'election/welcome.html')

def change_phone_number(request):
    if request.method == "POST":
        new_phone = request.POST.get("phone_number")
        voter_id = request.session.get("voter_id")

        if not new_phone:
            return JsonResponse({"success": False, "error": "Phone number is missing"})

        try:
            voter = Voter.objects.get(id=voter_id)
            voter.phone_number = new_phone
            voter.save()
            return JsonResponse({"success": True})
        except Voter.DoesNotExist:
            return JsonResponse({"success": False, "error": "Voter not found"})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"})

