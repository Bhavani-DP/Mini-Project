from django.shortcuts import render
from django.http import HttpResponse
from twilio.rest import Client
import random

# Dummy voter database
VOTER_DB = {
    '123456789012': {
        'uid': '123456789012',
        'name': 'Madhan',
        'dob': 'May 2, 1929',
        'photo_url': '/static/images/madhan.jpg',
        'phone': '968698XXXX'
    }
}

def home(request):
    return render(request, 'election/combined_form.html')

def verify_aadhaar(request):
    if request.method == 'POST':
        aadhaar = request.POST.get('aadhaar')
        voter = VOTER_DB.get(aadhaar)
        if voter:
            return render(request, 'election/voter_details.html', {'voter': voter})
        else:
            return HttpResponse("Invalid Aadhaar number.")
    return render(request, 'election/aadhaar_form.html')  

def send_otp(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone')
        to_number = '+91' + phone_number.strip()
        otp = str(random.randint(100000, 999999))

        account_sid = 'your_twilio_sid'
        auth_token = 'your_twilio_token'
        client = Client(account_sid, auth_token)

        try:
            client.messages.create(
                body=f"Your OTP is {otp}",
                from_='+1xxxxxxxxxx',
                to=to_number
            )
            return HttpResponse("OTP sent successfully.")
        except Exception as e:
            return HttpResponse(f"Twilio error: {str(e)}")
    