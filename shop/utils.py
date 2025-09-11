import random
from django.utils import timezone
from datetime import timedelta
from .models import PhoneOTP
from django.conf import settings

from django.conf import settings

import requests
from django.conf import settings

def send_sms_code(phone_number, code):
    url = "https://rest.nexmo.com/sms/json"
    payload = {
        "from": settings.VONAGE_SENDER_ID,
        "to": phone_number,
        "text": f"Your code: {code}",
        "api_key": settings.VONAGE_API_KEY,
        "api_secret": settings.VONAGE_API_SECRET,
    }

    response = requests.post(url, data=payload)
    data = response.json()

    if data["messages"][0]["status"] == "0":
        print(f"SMS надіслано на {phone_number}")
    else:
        print(f"Помилка: {data['messages'][0]['error-text']}")



def generate_sms_code(user):
    now = timezone.now()
    active_code = PhoneOTP.objects.filter(user=user, expires_at__gte=now).first()

    if active_code:
        print(f"DEBUG: Для {user.phone_number} вже є активний код -> {active_code.code}")
        return active_code.code

    code = str(random.randint(100000, 999999))
    expires = timezone.now() + timedelta(minutes=2)
    PhoneOTP.objects.create(user=user, code=code, expires_at=expires)

    print(f"DEBUG: Код для {user.phone_number} -> {code}")

    # send_sms_code(user, code)

    return code


def verify_sms_code(user, code):
    try:
        otp = PhoneOTP.objects.filter(user=user, code=code).latest('created_at')
    except PhoneOTP.DoesNotExist:
        return False
    
    if otp.is_valid():
        otp.delete()
        return True
    return False