import time
import webbrowser
from datetime import datetime

import pyautogui
from pywinauto import Desktop


GMAIL_URL = "https://mail.google.com/"

OPEN_WAIT = 5
SEARCH_WAIT = 3
ACTION_WAIT = 2

CURRENT_EMAIL_ROWS = []


# =========================================================
# BASIC HELPERS
# =========================================================

def get_text(control):
    try:
        return control.window_text().strip()
    except Exception:
        return ""


def get_name(control):
    try:
        return (control.element_info.name or "").strip()
    except Exception:
        return ""


def get_type(control):
    try:
        value = control.element_info.control_type
        return (value or "").lower()
    except Exception:
        return ""


def focus_window(window):
    if window is None:
        return False

    try:
        window.set_focus()
        time.sleep(0.5)
        return True
    except Exception:
        return False


def animated_click(control):
    try:
        rect = control.rectangle()

        if rect.width() <= 0 or rect.height() <= 0:
            return False

        x = rect.left + rect.width() // 2
        y = rect.top + rect.height() // 2

        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(0.15)
        pyautogui.click()

        return True

    except Exception:
        try:
            control.click_input()
            return True
        except Exception:
            return False


# =========================================================
# FIND GMAIL WINDOW
# =========================================================

def find_gmail_window():
    try:
        windows = Desktop(backend="uia").windows()
    except Exception:
        return None

    # First try window title.
    for window in windows:
        try:
            title = window.window_text().lower()

            if "gmail" in title:
                return window
        except Exception:
            continue

    # Fallback using Gmail controls.
    for window in windows:
        try:
            texts = set()

            for control in window.descendants():
                text = get_text(control).lower()

                if text:
                    texts.add(text)

            if "inbox" in texts and "sent" in texts:
                return window

        except Exception:
            continue

    return None


# =========================================================
# FIND CONTROL
# =========================================================

def find_control(text, window=None):
    if window is None:
        window = find_gmail_window()

    if window is None:
        return None

    target = text.strip().lower()

    try:
        controls = window.descendants()
    except Exception:
        return None

    # Exact match first.
    for control in controls:
        text_value = get_text(control).lower()
        name_value = get_name(control).lower()

        if text_value == target:
            return control

        if name_value == target:
            return control

    # Partial match second.
    for control in controls:
        text_value = get_text(control).lower()
        name_value = get_name(control).lower()

        if target in text_value and text_value:
            return control

        if target in name_value and name_value:
            return control

    return None


# =========================================================
# OPEN GMAIL
# =========================================================

def open_gmail() -> dict:
    try:
        window = find_gmail_window()

        if window is not None:
            focus_window(window)

            return {
                "status": "success",
                "message": "Existing Gmail focused."
            }

        webbrowser.open(GMAIL_URL, new=0)
        time.sleep(OPEN_WAIT)

        window = find_gmail_window()

        if window is None:
            return {
                "status": "error",
                "message": "Gmail could not be detected."
            }

        focus_window(window)

        return {
            "status": "success",
            "message": "Gmail opened."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# SEARCH GMAIL
# =========================================================

def search_gmail(query: str) -> dict:
    global CURRENT_EMAIL_ROWS

    query = query.strip()

    if not query:
        return {
            "status": "error",
            "message": "Search query is empty."
        }

    result = open_gmail()

    if result["status"] != "success":
        return result

    try:
        window = find_gmail_window()

        if window is None:
            return {
                "status": "error",
                "message": "Gmail window was not found."
            }

        focus_window(window)

        pyautogui.press("/")
        time.sleep(0.5)

        pyautogui.hotkey("ctrl", "a")
        pyautogui.write(query, interval=0.03)
        pyautogui.press("enter")

        time.sleep(SEARCH_WAIT)

        CURRENT_EMAIL_ROWS = []

        return {
            "status": "success",
            "query": query
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


def search_today_emails() -> dict:
    today = datetime.now().strftime("%Y/%m/%d")

    return search_gmail(
        f"after:{today}"
    )


# =========================================================
# EMAIL ROW DETECTION
# =========================================================

def looks_like_email_row(control):
    try:
        control_type = get_type(control)

        allowed = {
            "dataitem",
            "listitem",
            "treeitem",
            "custom"
        }

        if control_type not in allowed:
            return False

        rect = control.rectangle()

        if rect.width() < 350:
            return False

        if rect.height() < 20 or rect.height() > 130:
            return False

        texts = []

        for child in control.descendants():
            text = get_text(child)

            if text and text not in texts:
                texts.append(text)

        if len(texts) < 2:
            return False

        combined = " ".join(texts).lower()

        ignored = [
            "compose inbox starred",
            "sent drafts",
            "google apps",
            "settings"
        ]

        if any(item in combined for item in ignored):
            return False

        return True

    except Exception:
        return False


def get_row_texts(control):
    texts = []

    try:
        for child in control.descendants():
            text = get_text(child)

            if text and text not in texts:
                texts.append(text)
    except Exception:
        pass

    own_text = get_text(control)

    if own_text and own_text not in texts:
        texts.insert(0, own_text)

    return texts


def get_email_rows() -> dict:
    global CURRENT_EMAIL_ROWS

    window = find_gmail_window()

    if window is None:
        return {
            "status": "error",
            "message": "Gmail was not found."
        }

    try:
        focus_window(window)

        candidates = []

        for control in window.descendants():
            if looks_like_email_row(control):
                candidates.append(control)

        rows = []
        seen = set()

        for control in candidates:
            try:
                rect = control.rectangle()

                key = (
                    rect.left,
                    rect.top,
                    rect.right,
                    rect.bottom
                )

                if key in seen:
                    continue

                seen.add(key)
                rows.append(control)

            except Exception:
                continue

        rows.sort(
            key=lambda item: item.rectangle().top
        )

        CURRENT_EMAIL_ROWS = rows

        emails = []

        for index, row in enumerate(rows):
            emails.append({
                "index": index,
                "text": get_row_texts(row)
            })

        return {
            "status": "success",
            "count": len(emails),
            "emails": emails
        }

    except Exception as error:
        CURRENT_EMAIL_ROWS = []

        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# COUNT TODAY
# =========================================================

def count_today_emails() -> dict:
    result = search_today_emails()

    if result["status"] != "success":
        return result

    rows = get_email_rows()

    if rows["status"] != "success":
        return rows

    return {
        "status": "success",
        "count": rows["count"],
        "message": (
            f'{rows["count"]} email(s) found today.'
        )
    }


# =========================================================
# OPEN EMAIL
# =========================================================

def open_email_by_index(index: int) -> dict:
    global CURRENT_EMAIL_ROWS

    try:
        index = int(index)

        if not CURRENT_EMAIL_ROWS:
            result = get_email_rows()

            if result["status"] != "success":
                return result

        if index < 0 or index >= len(CURRENT_EMAIL_ROWS):
            return {
                "status": "error",
                "message": "Email index does not exist."
            }

        window = find_gmail_window()

        if window is None:
            return {
                "status": "error",
                "message": "Gmail window was not found."
            }

        focus_window(window)

        row = CURRENT_EMAIL_ROWS[index]

        if not animated_click(row):
            return {
                "status": "error",
                "message": "Could not open email."
            }

        time.sleep(ACTION_WAIT)

        return {
            "status": "success",
            "index": index
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# READ OPEN EMAIL
# =========================================================

def read_open_email() -> dict:
    window = find_gmail_window()

    if window is None:
        return {
            "status": "error",
            "message": "Gmail was not found."
        }

    try:
        focus_window(window)

        texts = []

        ignored = {
            "compose",
            "inbox",
            "starred",
            "snoozed",
            "sent",
            "drafts",
            "more",
            "meet",
            "chat"
        }

        for control in window.descendants():
            text = get_text(control)

            if not text:
                continue

            if text.lower() in ignored:
                continue

            if text not in texts:
                texts.append(text)

        content = "\n".join(texts)

        return {
            "status": "success",
            "content": content[:5000]
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# GO BACK
# =========================================================

def go_back_to_mail_list() -> dict:
    try:
        window = find_gmail_window()

        if window is not None:
            focus_window(window)

        pyautogui.hotkey("alt", "left")
        time.sleep(ACTION_WAIT)

        return {
            "status": "success"
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# SEND CURRENT COMPOSE
#
# Gmail compose body must already be focused.
# Ctrl + Enter sends from the active compose.
# =========================================================

def send_current_compose(window) -> dict:
    try:
        if window is None:
            return {
                "status": "error",
                "message": "Gmail window was not found."
            }

        focus_window(window)

        # The body editor should still be focused.
        pyautogui.hotkey("ctrl", "enter")

        time.sleep(1)

        # Gmail may show a Ctrl+Enter confirmation dialog.
        confirm = find_control(
            "Send",
            window
        )

        if confirm is not None:
            try:
                control_type = get_type(confirm)

                if control_type == "button":
                    animated_click(confirm)
                    time.sleep(1)
            except Exception:
                pass

        return {
            "status": "success",
            "message": "Send command completed."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# SEND NEW EMAIL
#
# The user already said SEND.
# No second confirmation.
# =========================================================

def send_new_email(
    to: str,
    subject: str,
    body: str
) -> dict:

    to = to.strip()
    subject = subject.strip()
    body = body.strip()

    if not to:
        return {
            "status": "error",
            "message": "Recipient is required."
        }

    if not body:
        return {
            "status": "error",
            "message": "Email body is empty."
        }

    result = open_gmail()

    if result["status"] != "success":
        return result

    try:
        window = find_gmail_window()

        if window is None:
            return {
                "status": "error",
                "message": "Gmail window was not found."
            }

        focus_window(window)

        # -------------------------------------------------
        # COMPOSE
        # -------------------------------------------------

        compose = find_control(
            "Compose",
            window
        )

        if compose is None:
            return {
                "status": "error",
                "message": "Compose button was not found."
            }

        if not animated_click(compose):
            return {
                "status": "error",
                "message": "Could not click Compose."
            }

        time.sleep(1.2)

        # -------------------------------------------------
        # RECIPIENT
        # -------------------------------------------------

        pyautogui.write(
            to,
            interval=0.03
        )

        time.sleep(0.2)

        pyautogui.press("enter")

        time.sleep(0.3)

        # Move from recipient to subject.
        pyautogui.press("tab")

        time.sleep(0.2)

        # -------------------------------------------------
        # SUBJECT
        # -------------------------------------------------

        pyautogui.write(
            subject,
            interval=0.03
        )

        time.sleep(0.2)

        # Move from subject to body.
        pyautogui.press("tab")

        time.sleep(0.3)

        # -------------------------------------------------
        # BODY
        # -------------------------------------------------

        pyautogui.write(
            body,
            interval=0.015
        )

        time.sleep(0.7)

        # -------------------------------------------------
        # SEND
        #
        # Do NOT search accessibility tree for Send.
        # Send from the currently focused compose.
        # -------------------------------------------------

        send_result = send_current_compose(
            window
        )

        if send_result["status"] != "success":
            return send_result

        time.sleep(2)

        return {
            "status": "success",
            "to": to,
            "subject": subject,
            "message": "Email sent successfully."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# REPLY AND SEND
# =========================================================

def reply_and_send(body: str) -> dict:
    body = body.strip()

    if not body:
        return {
            "status": "error",
            "message": "Reply body is empty."
        }

    window = find_gmail_window()

    if window is None:
        return {
            "status": "error",
            "message": "Gmail was not found."
        }

    try:
        focus_window(window)

        # -------------------------------------------------
        # REPLY
        # -------------------------------------------------

        reply = find_control(
            "Reply",
            window
        )

        if reply is None:
            return {
                "status": "error",
                "message": "Reply button was not found."
            }

        if not animated_click(reply):
            return {
                "status": "error",
                "message": "Could not click Reply."
            }

        time.sleep(1)

        # -------------------------------------------------
        # BODY
        # -------------------------------------------------

        pyautogui.write(
            body,
            interval=0.015
        )

        time.sleep(0.7)

        # -------------------------------------------------
        # SEND
        # -------------------------------------------------

        send_result = send_current_compose(
            window
        )

        if send_result["status"] != "success":
            return send_result

        time.sleep(2)

        return {
            "status": "success",
            "message": "Reply sent successfully."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }