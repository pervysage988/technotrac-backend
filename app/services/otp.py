# app/services/otp.py
import random
import json
from datetime import datetime, timedelta
import os

from fastapi import HTTPException
from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client  # ✅ Twilio SDK

from app.core.redis import set_value, get_value, delete_value
from app.core.logging import logger, mask_phone
from app.db.models.otp_code import OtpCode


# OTP Config
OTP_TTL_SECONDS = 300       # 5 minutes
RATE_LIMIT_SECONDS = 60     # 1 minute between OTP requests
HOURLY_LIMIT = 5            # max 5 requests per hour


# SMS provider settings
SMS_PROVIDER = os.getenv("SMS_PROVIDER", "twilio").lower()

# Twilio settings
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


async def send_otp(phone: str, session: AsyncSession) -> None:
    """Generate OTP, enforce rate limits, save in Redis + Postgres, send via SMS."""

    # --- Rate limiting ---
    rate_key = f"otp:rate:{phone}"
    hourly_key = f"otp:hourly:{phone}"

    if await get_value(rate_key):
        raise HTTPException(
            status_code=429,
            detail="OTP already sent, please wait 1 minute before retrying."
        )

    hourly_count = await get_value(hourly_key)
    if hourly_count and int(hourly_count) >= HOURLY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many OTP requests, please try again in an hour."
        )

    # --- Generate OTP ---
    code = str(random.randint(100000, 999999))
    otp_key = f"otp:{phone}"
    otp_data = {"code": code, "attempts": 0}

    await set_value(otp_key, json.dumps(otp_data), OTP_TTL_SECONDS)
    await set_value(rate_key, "1", RATE_LIMIT_SECONDS)

    if not hourly_count:
        await set_value(hourly_key, "1", 3600)
    else:
        new_count = int(hourly_count) + 1
        await set_value(hourly_key, str(new_count), 3600)

    # Store in Postgres for audit
    expires_at = datetime.utcnow() + timedelta(seconds=OTP_TTL_SECONDS)
    record = OtpCode(
        phone_e164=phone,
        code_hash=bcrypt.hash(code),
        expires_at=expires_at,
    )
    session.add(record)
    await session.commit()

    # --- Send OTP ---
    try:
        if SMS_PROVIDER == "twilio":
            if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_NUMBER):
                raise RuntimeError("Twilio credentials not set in environment.")

            client = Client(TWILIO_SID, TWILIO_TOKEN)
            message = client.messages.create(
                body=f"Your TechnoTrac OTP is {code}. It expires in 5 minutes.",
                from_=TWILIO_NUMBER,
                to=phone,
            )
            logger.info(f"✅ OTP sent via Twilio to {mask_phone(phone)} (sid={message.sid})")

        else:
            # Fallback: only log (useful for dev/testing)
            logger.info(f"[DEV] OTP for {mask_phone(phone)}: {code}")

    except Exception as e:
        logger.error(f"❌ Failed to send OTP to {mask_phone(phone)}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP")


async def verify_otp(phone: str, code: str) -> bool:
    """Verify OTP from Redis and limit attempts."""
    otp_key = f"otp:{phone}"
    raw = await get_value(otp_key)
    if not raw:
        return False

    otp_data = json.loads(raw)

    if otp_data["attempts"] >= 5:
        await delete_value(otp_key)
        raise HTTPException(status_code=400, detail="Too many attempts, request a new OTP.")

    if otp_data["code"] != code:
        otp_data["attempts"] += 1
        await set_value(otp_key, json.dumps(otp_data), OTP_TTL_SECONDS)
        logger.warning(f"⚠️ Invalid OTP attempt for {mask_phone(phone)}")
        return False

    await delete_value(otp_key)
    logger.info(f"✅ OTP verified successfully for {mask_phone(phone)}")
    return True
