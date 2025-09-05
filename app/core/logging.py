import logging
import re

# -----------------------------
# Masking utilities
# -----------------------------
def mask_phone(phone: str) -> str:
    """Mask phone number for logs, keep only country code + last 3 digits."""
    if not phone:
        return phone
    return re.sub(r"(\+\d{1,3})(\d+)(\d{3})", r"\1******\3", phone)


def mask_upi(upi: str) -> str:
    """Mask UPI IDs for logs, hide most of the user part but keep domain."""
    if not upi or "@" not in upi:
        return "***"
    user, domain = upi.split("@", 1)
    if len(user) <= 2:
        masked_user = "*" * len(user)
    else:
        masked_user = user[0] + "*" * (len(user) - 2) + user[-1]
    return f"{masked_user}@{domain}"


# -----------------------------
# PII filter for all logs
# -----------------------------
class PiiFilter(logging.Filter):
    """Custom log filter to mask phone numbers, OTPs, and UPI IDs automatically."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg

            # Mask phone numbers (+91..., +120..., etc.)
            msg = re.sub(
                r"(\+\d{1,3}\d{7,12})",
                lambda m: mask_phone(m.group(1)),
                msg,
            )

            # Mask UPI IDs
            msg = re.sub(
                r"\b[\w.\-]+@[\w\-]+\b",
                lambda m: mask_upi(m.group(0)),
                msg,
            )

            # Redact OTPs (6-digit codes)
            msg = re.sub(r"\b\d{6}\b", "[OTP-REDACTED]", msg)

            record.msg = msg
            record.args = ()
        return True


# -----------------------------
# Logger setup
# -----------------------------
def get_logger(name: str = "technotrac") -> logging.Logger:
    logger = logging.getLogger(name)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        handler.addFilter(PiiFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# Default project logger
logger = get_logger()
