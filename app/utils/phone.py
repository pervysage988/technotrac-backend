# app/utils/phone.py (final)
import phonenumbers
from fastapi import HTTPException
from app.core.logging import logger, mask_phone

def validate_phone_e164(phone: str) -> str:
    """
    Validate phone number and return in E.164 format.
    Example: "+919876543210"
    """
    try:
        parsed = phonenumbers.parse(phone, None)
        if not phonenumbers.is_possible_number(parsed) or not phonenumbers.is_valid_number(parsed):
            raise ValueError("Invalid phone number")

        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        logger.warning(f"Invalid phone input attempted: {mask_phone(phone)}")
        raise HTTPException(status_code=400, detail="Invalid phone number format")
