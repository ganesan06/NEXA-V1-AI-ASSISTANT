import os
import time
import pyautogui

from urllib.parse import quote

from .contacts import get_phone_number


# =========================================================
# WHATSAPP - PREPARE
# =========================================================

def prepare_whatsapp_message(
    contact_name: str,
    message: str
) -> dict:
    """Prepare a WhatsApp message without sending."""

    phone_number = get_phone_number(contact_name)

    if not phone_number:

        return {
            "status": "error",
            "message": f"{contact_name} was not found in contacts."
        }

    clean_number = (
        phone_number
        .replace("+", "")
        .replace(" ", "")
        .replace("-", "")
    )

    encoded_message = quote(message)

    whatsapp_url = (
        f"whatsapp://send"
        f"?phone={clean_number}"
        f"&text={encoded_message}"
    )

    try:

        os.startfile(whatsapp_url)

        return {
            "status": "success",
            "message": f"Message prepared for {contact_name}."
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# WHATSAPP - SEND
# =========================================================

def send_whatsapp_message(
    contact_name: str,
    message: str
) -> dict:
    """Open WhatsApp and send a message."""

    phone_number = get_phone_number(contact_name)

    if not phone_number:

        return {
            "status": "error",
            "message": f"{contact_name} was not found in contacts."
        }

    clean_number = (
        phone_number
        .replace("+", "")
        .replace(" ", "")
        .replace("-", "")
    )

    encoded_message = quote(message)

    whatsapp_url = (
        f"whatsapp://send"
        f"?phone={clean_number}"
        f"&text={encoded_message}"
    )

    try:

        os.startfile(whatsapp_url)

        time.sleep(4)

        pyautogui.press("enter")

        return {
            "status": "success",
            "message": f"Message sent to {contact_name}."
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# TELEGRAM - OPEN
# =========================================================

def open_telegram() -> dict:
    """Open Telegram Desktop."""

    try:

        os.startfile("tg:")

        return {
            "status": "success",
            "message": "Telegram opened."
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# TELEGRAM - SEND
# =========================================================

def send_telegram_message(
    contact_name: str,
    message: str
) -> dict:
    """
    Telegram sending will be connected later.
    """

    return {
        "status": "setup_required",
        "message": (
            f"Telegram sending to {contact_name} "
            "is not configured yet."
        )
    }


# =========================================================
# GMAIL
# =========================================================

def send_gmail(
    recipient_email: str,
    subject: str,
    message: str
) -> dict:
    """
    Gmail sending will use authenticated
    Gmail integration later.
    """

    if "@" not in recipient_email:

        return {
            "status": "error",
            "message": "A valid email address is required."
        }

    return {
        "status": "setup_required",
        "message": (
            "Gmail authentication has not "
            "been configured yet."
        )
    }