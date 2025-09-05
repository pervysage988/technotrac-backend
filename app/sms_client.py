 
# app/sms_client.py
from abc import ABC, abstractmethod
from typing import Any
import requests
from .settings import settings

class SMSClient(ABC):
    @abstractmethod
    def send_sms(self, to_e164: str, message: str) -> None: ...

class TwilioClient(SMSClient):
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        from twilio.rest import Client
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def send_sms(self, to_e164: str, message: str) -> None:
        self.client.messages.create(to=to_e164, from_=self.from_number, body=message)

class MSG91Client(SMSClient):
    def __init__(self, auth_key: str, sender_id: str, template_id: str | None = None):
        self.auth_key = auth_key
        self.sender_id = sender_id
        self.template_id = template_id

    def send_sms(self, to_e164: str, message: str) -> None:
        mobile = to_e164.lstrip("+")
        url = (
            "https://api.msg91.com/api/v5/flow/"
            if self.template_id
            else "https://api.msg91.com/api/v2/sendsms"
        )
        headers = {
            "accept": "application/json",
            "authkey": self.auth_key,
            "content-type": "application/json",
        }

        if self.template_id:
            payload: dict[str, Any] = {
                "template_id": self.template_id,
                "short_url": "0",
                "recipients": [{"mobiles": mobile, "message": message}],
            }
        else:
            payload = {
                "sender": self.sender_id,
                "route": "4",
                "country": "91",
                "sms": [{"message": message, "to": [mobile]}],
            }

        r = requests.post(url, json=payload, headers=headers, timeout=10)
        r.raise_for_status()

def get_sms_client() -> SMSClient:
    if settings.SMS_PROVIDER == "twilio":
        if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER):
            raise RuntimeError("Twilio config missing")
        return TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER)
    elif settings.SMS_PROVIDER == "msg91":
        if not (settings.MSG91_AUTH_KEY and settings.MSG91_SENDER_ID):
            raise RuntimeError("MSG91 config missing")
        return MSG91Client(settings.MSG91_AUTH_KEY, settings.MSG91_SENDER_ID, settings.MSG91_TEMPLATE_ID)
    raise RuntimeError("Unknown SMS_PROVIDER")
