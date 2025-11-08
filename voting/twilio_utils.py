from twilio.rest import Client
from django.conf import settings

def send_otp_sms(phone_number, otp):
    print(f"📲 Sending OTP {otp} to {phone_number}")
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    print(f"✅ Message SID: {message.sid}")
    return message.sid