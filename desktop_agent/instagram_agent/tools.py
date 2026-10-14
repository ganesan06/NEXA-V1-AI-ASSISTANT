import os
import subprocess
import threading
import time

import pyautogui
from google import genai
from pywinauto import Desktop


INSTAGRAM_URL = "https://www.instagram.com/"
INSTAGRAM_DM_URL = "https://www.instagram.com/direct/inbox/"

OPEN_WAIT = 5
ACTION_WAIT = 2
CHECK_INTERVAL = 4


# =========================================================
# CONVERSATION STATE
# =========================================================

CONVERSATION_STATE = {
    "active": False,
    "username": None,
    "history": [],
    "last_incoming_signature": None,
    "status": "stopped"
}

conversation_thread = None
conversation_lock = threading.Lock()


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


def focus_window(window):
    if window is None:
        return False

    try:
        window.set_focus()
        time.sleep(0.4)
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
        time.sleep(0.2)
        pyautogui.click()

        return True

    except Exception:
        try:
            control.click_input()
            return True
        except Exception:
            return False


# =========================================================
# FIND INSTAGRAM WINDOW
# =========================================================

def find_instagram_window():
    try:
        windows = Desktop(backend="uia").windows()
    except Exception:
        return None

    for window in windows:
        try:
            title = window.window_text().lower()

            if "instagram" in title:
                return window
        except Exception:
            continue

    return None


# =========================================================
# FIND CONTROL
# =========================================================

def find_control(target_text, window):
    target = target_text.strip().lower()

    try:
        controls = window.descendants()
    except Exception:
        return None

    # Exact match first.
    for control in controls:
        text = get_text(control).lower()
        name = get_name(control).lower()

        if text == target or name == target:
            return control

    # Partial match second.
    for control in controls:
        text = get_text(control).lower()
        name = get_name(control).lower()

        if text and target in text:
            return control

        if name and target in name:
            return control

    return None


# =========================================================
# CREATE INSTAGRAM WINDOW
# =========================================================

def create_instagram_window() -> dict:
    existing = find_instagram_window()

    if existing is not None:
        focus_window(existing)

        return {
            "status": "success",
            "message": "Instagram window focused."
        }

    try:
        subprocess.Popen([
            "cmd",
            "/c",
            "start",
            "",
            "chrome",
            "--new-window",
            INSTAGRAM_URL
        ])

        time.sleep(OPEN_WAIT)

        window = find_instagram_window()

        if window is None:
            return {
                "status": "error",
                "message": "Instagram window was not detected."
            }

        focus_window(window)

        return {
            "status": "success",
            "message": "Instagram opened."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# OPEN INSTAGRAM
# =========================================================

def open_instagram() -> dict:
    window = find_instagram_window()

    if window is not None:
        focus_window(window)

        return {
            "status": "success",
            "message": "Instagram focused."
        }

    return create_instagram_window()


# =========================================================
# NAVIGATE INSTAGRAM
# =========================================================

def navigate_instagram(url: str) -> dict:
    window = find_instagram_window()

    if window is None:
        result = create_instagram_window()

        if result["status"] != "success":
            return result

        window = find_instagram_window()

    if window is None:
        return {
            "status": "error",
            "message": "Instagram window not found."
        }

    try:
        focus_window(window)

        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.2)

        pyautogui.write(url, interval=0.01)
        pyautogui.press("enter")

        time.sleep(OPEN_WAIT)

        return {
            "status": "success"
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# OPEN INSTAGRAM DMS
# =========================================================

def open_instagram_dms() -> dict:
    result = navigate_instagram(INSTAGRAM_DM_URL)

    if result["status"] != "success":
        return result

    return {
        "status": "success",
        "message": "Instagram DMs opened."
    }


# =========================================================
# OPEN PERSON'S DM
# =========================================================

def open_dm(username: str) -> dict:
    username = username.strip()

    if not username:
        return {
            "status": "error",
            "message": "Conversation name required."
        }

    result = open_instagram_dms()

    if result["status"] != "success":
        return result

    window = find_instagram_window()

    if window is None:
        return {
            "status": "error",
            "message": "Instagram window not found."
        }

    focus_window(window)
    time.sleep(ACTION_WAIT)

    conversation = find_control(username, window)

    if conversation is None:
        return {
            "status": "error",
            "message": f'Could not find "{username}".'
        }

    if not animated_click(conversation):
        return {
            "status": "error",
            "message": "Could not open conversation."
        }

    time.sleep(2)

    return {
        "status": "success",
        "username": username,
        "message": f'Opened DM with "{username}".'
    }


# =========================================================
# FILTER INSTAGRAM UI TEXT
# =========================================================

def is_valid_message_text(text: str) -> bool:
    text = text.strip()

    if not text:
        return False

    lower = text.lower()

    ignored = {
        "message",
        "message...",
        "home",
        "search",
        "explore",
        "reels",
        "messages",
        "notifications",
        "create",
        "profile",
        "more",
        "seen",
        "reply",
        "forward",
        "like",
        "user-profile-picture"
    }

    if lower in ignored:
        return False

    # Accessibility labels, not real messages.
    if lower.startswith("see more options"):
        return False

    if "user-profile-picture" in lower:
        return False

    # Instagram reply-preview labels.
    if "replied to you" in lower:
        return False

    if "you replied" in lower:
        return False

    # Seen labels.
    if lower.startswith("seen "):
        return False

    # Basic time labels.
    if lower.endswith(" am") or lower.endswith(" pm"):
        return False

    return True


# =========================================================
# GET INCOMING MESSAGE CANDIDATES
# =========================================================

def get_incoming_candidates():
    window = find_instagram_window()

    if window is None:
        return []

    try:
        window_rect = window.rectangle()

        width = window_rect.width()
        height = window_rect.height()

        # Conversation area starts around the middle.
        conversation_left = window_rect.left + int(width * 0.50)

        # Incoming bubbles are on the left side
        # of the conversation panel.
        incoming_right = window_rect.left + int(width * 0.73)

        top_limit = window_rect.top + int(height * 0.10)
        bottom_limit = window_rect.top + int(height * 0.92)

        candidates = []

        for control in window.descendants():
            try:
                text = get_text(control).strip()

                if not is_valid_message_text(text):
                    continue

                rect = control.rectangle()

                if rect.width() <= 0 or rect.height() <= 0:
                    continue

                if rect.left < conversation_left:
                    continue

                if rect.left > incoming_right:
                    continue

                if rect.top < top_limit:
                    continue

                if rect.bottom > bottom_limit:
                    continue

                # Ignore large containers, reels, panels, etc.
                if rect.width() > width * 0.35:
                    continue

                if rect.height() > height * 0.12:
                    continue

                candidates.append({
                    "text": text,
                    "top": rect.top,
                    "left": rect.left,
                    "right": rect.right
                })

            except Exception:
                continue

        # Remove duplicate UIA controls.
        unique = []

        for item in candidates:
            duplicate = False

            for saved in unique:
                same_text = item["text"] == saved["text"]
                close_y = abs(item["top"] - saved["top"]) < 8

                if same_text and close_y:
                    duplicate = True
                    break

            if not duplicate:
                unique.append(item)

        unique.sort(key=lambda item: item["top"])

        return unique

    except Exception:
        return []


# =========================================================
# READ LATEST INCOMING MESSAGE
# =========================================================

def read_latest_incoming_message() -> dict:
    candidates = get_incoming_candidates()

    if not candidates:
        return {
            "status": "error",
            "message": "No incoming message found."
        }

    latest = candidates[-1]

    text = latest["text"]

    # Text + current vertical position.
    signature = f'{latest["top"]}:{text}'

    return {
        "status": "success",
        "message": text,
        "signature": signature
    }


# =========================================================
# READ CURRENT DM
# =========================================================

def read_current_dm() -> dict:
    candidates = get_incoming_candidates()

    messages = [
        item["text"]
        for item in candidates
    ]

    return {
        "status": "success",
        "messages": messages[-10:]
    }


# =========================================================
# READ LATEST MESSAGE
# =========================================================

def read_latest_message() -> dict:
    result = read_latest_incoming_message()

    if result["status"] != "success":
        return result

    return {
        "status": "success",
        "latest_message": result["message"]
    }


# =========================================================
# READ LATEST MESSAGE FROM PERSON
# =========================================================

def read_latest_dm_from(username: str) -> dict:
    result = open_dm(username)

    if result["status"] != "success":
        return result

    time.sleep(1)

    result = read_latest_incoming_message()

    if result["status"] != "success":
        return result

    return {
        "status": "success",
        "username": username,
        "latest_message": result["message"]
    }


# =========================================================
# FOCUS MESSAGE INPUT
# =========================================================

def focus_message_input() -> dict:
    window = find_instagram_window()

    if window is None:
        return {
            "status": "error",
            "message": "Instagram window not found."
        }

    try:
        focus_window(window)

        rect = window.rectangle()

        width = rect.width()
        height = rect.height()

        # These coordinates worked with your
        # current Instagram layout.
        x = rect.left + int(width * 0.68)
        y = rect.top + int(height * 0.97)

        pyautogui.moveTo(x, y, duration=0.5)

        time.sleep(0.2)
        pyautogui.click()
        time.sleep(0.4)

        return {
            "status": "success"
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# TYPE INSTAGRAM MESSAGE
# =========================================================

def type_instagram_message(message: str) -> dict:
    message = message.strip()

    if not message:
        return {
            "status": "error",
            "message": "Message is empty."
        }

    result = focus_message_input()

    if result["status"] != "success":
        return result

    try:
        pyautogui.write(message, interval=0.05)

        return {
            "status": "success",
            "message": "Message typed."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# SEND CURRENT INSTAGRAM MESSAGE
# =========================================================

def send_current_instagram_message(message: str) -> dict:
    message = message.strip()

    if not message:
        return {
            "status": "error",
            "message": "Message is empty."
        }

    result = type_instagram_message(message)

    if result["status"] != "success":
        return result

    try:
        time.sleep(0.3)

        pyautogui.press("enter")

        time.sleep(1)

        return {
            "status": "success",
            "message": "Instagram send command completed."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# =========================================================
# SEND MESSAGE TO PERSON
# =========================================================

def send_instagram_message(username: str, message: str) -> dict:
    username = username.strip()
    message = message.strip()

    if not username:
        return {
            "status": "error",
            "message": "Recipient required."
        }

    if not message:
        return {
            "status": "error",
            "message": "Message is empty."
        }

    result = open_dm(username)

    if result["status"] != "success":
        return result

    time.sleep(1)

    result = send_current_instagram_message(message)

    if result["status"] != "success":
        return result

    return {
        "status": "success",
        "username": username,
        "message_text": message
    }


# =========================================================
# CLEAN HISTORY
# =========================================================

def add_history(role: str, text: str):
    text = text.strip()

    if not text:
        return

    with conversation_lock:
        history = CONVERSATION_STATE["history"]

        # Don't add the same message twice in a row.
        if history:
            last = history[-1]

            if last["role"] == role and last["text"] == text:
                return

        history.append({
            "role": role,
            "text": text
        })

        # Keep only recent conversation.
        if len(history) > 20:
            CONVERSATION_STATE["history"] = history[-20:]


# =========================================================
# BUILD CLEAN HISTORY
# =========================================================

def build_clean_history():
    with conversation_lock:
        history = list(CONVERSATION_STATE["history"])

    lines = []

    for item in history[-10:]:
        speaker = "Them" if item["role"] == "them" else "Me"
        lines.append(f'{speaker}: {item["text"]}')

    return "\n".join(lines)


# =========================================================
# GENERATE CONVERSATION REPLY
# =========================================================

def generate_conversation_reply(username: str, incoming_message: str):
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("[Instagram] GOOGLE_API_KEY missing.")
        return None

    history = build_clean_history()

    prompt = f"""
You are writing one reply in a casual Instagram DM.

Person:
{username}

Conversation:
{history}

Their newest message:
{incoming_message}

Write ONLY the message to send.

Rules:
- Reply directly to their newest message.
- Understand the newest message using the conversation.
- Do not suddenly change the topic.
- If they ask a question, answer that question.
- If the message is unclear, ask a short clarification.
- Never invent facts about me.
- Never invent my personal identity or personal details.
- Do not send unrelated filler.
- Do not repeat something I already said.
- Keep the reply casual and natural.
- Usually use one short sentence.
- Do not explain your reasoning.
- Do not write "Reply:".
- Do not put quotation marks around the reply.
"""

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        reply = (response.text or "").strip()

        if not reply:
            return None

        if len(reply) > 300:
            return None

        return reply

    except Exception as error:
        print("[Instagram] Gemini error:", error)
        return None


# =========================================================
# CONVERSATION WORKER
# =========================================================

def instagram_conversation_worker():
    print()
    print("[Instagram] Conversation started.")

    while True:
        with conversation_lock:
            active = CONVERSATION_STATE["active"]
            username = CONVERSATION_STATE["username"]
            old_signature = CONVERSATION_STATE["last_incoming_signature"]

        if not active:
            break

        try:
            result = read_latest_incoming_message()

            if result["status"] != "success":
                time.sleep(CHECK_INTERVAL)
                continue

            incoming = result["message"].strip()
            signature = result["signature"]

            # Same incoming bubble as last check.
            if signature == old_signature:
                time.sleep(CHECK_INTERVAL)
                continue

            # Mark it immediately so the same
            # bubble cannot trigger twice.
            with conversation_lock:
                CONVERSATION_STATE["last_incoming_signature"] = signature
                CONVERSATION_STATE["status"] = "thinking"

            add_history("them", incoming)

            print()
            print("[Instagram] THEM:")
            print(incoming)

            print()
            print("[Instagram] CLEAN HISTORY:")
            print(build_clean_history())

            reply = generate_conversation_reply(
                username,
                incoming
            )

            if not reply:
                with conversation_lock:
                    CONVERSATION_STATE["status"] = "waiting"

                time.sleep(CHECK_INTERVAL)
                continue

            # User might have stopped the conversation
            # while Gemini was generating the reply.
            with conversation_lock:
                still_active = CONVERSATION_STATE["active"]

            if not still_active:
                break

            print()
            print("[Instagram] ME:")
            print(reply)

            with conversation_lock:
                CONVERSATION_STATE["status"] = "sending"

            send_result = send_current_instagram_message(reply)

            if send_result["status"] == "success":
                # We know exactly what we sent.
                # Store it ourselves instead of reading
                # our blue bubble from Instagram.
                add_history("me", reply)

                with conversation_lock:
                    CONVERSATION_STATE["status"] = "waiting"

                print("[Instagram] Reply sent.")

            else:
                print("[Instagram] Send failed:", send_result)

                with conversation_lock:
                    CONVERSATION_STATE["status"] = "waiting"

        except Exception as error:
            print("[Instagram] Worker error:", error)

        time.sleep(CHECK_INTERVAL)

    print()
    print("[Instagram] Conversation stopped.")


# =========================================================
# START CONVERSATION
# =========================================================

def start_instagram_conversation(username: str) -> dict:
    global conversation_thread

    username = username.strip()

    if not username:
        return {
            "status": "error",
            "message": "Conversation name required."
        }

    with conversation_lock:
        if CONVERSATION_STATE["active"]:
            current_user = CONVERSATION_STATE["username"]

            return {
                "status": "error",
                "message": f'Conversation with "{current_user}" is already running.'
            }

    # Open the correct person's DM.
    result = open_dm(username)

    if result["status"] != "success":
        return result

    time.sleep(1)

    # Current incoming bubble becomes the baseline.
    # The worker waits for the NEXT incoming message.
    baseline = read_latest_incoming_message()

    baseline_signature = None

    if baseline["status"] == "success":
        baseline_signature = baseline["signature"]

    with conversation_lock:
        CONVERSATION_STATE["active"] = True
        CONVERSATION_STATE["username"] = username
        CONVERSATION_STATE["history"] = []
        CONVERSATION_STATE["last_incoming_signature"] = baseline_signature
        CONVERSATION_STATE["status"] = "waiting"

    conversation_thread = threading.Thread(
        target=instagram_conversation_worker,
        daemon=True
    )

    conversation_thread.start()

    return {
        "status": "success",
        "username": username,
        "message": (
            f'Conversation mode started with "{username}". '
            "Waiting for their next message."
        )
    }


# =========================================================
# STOP CONVERSATION
# =========================================================

def stop_instagram_conversation() -> dict:
    with conversation_lock:
        username = CONVERSATION_STATE["username"]
        active = CONVERSATION_STATE["active"]

        CONVERSATION_STATE["active"] = False
        CONVERSATION_STATE["status"] = "stopped"

    if not active:
        return {
            "status": "success",
            "message": "Conversation mode is already stopped."
        }

    return {
        "status": "success",
        "message": f'Conversation with "{username}" stopped.'
    }


# =========================================================
# CONVERSATION STATUS
# =========================================================

def get_instagram_conversation_status() -> dict:
    with conversation_lock:
        history = list(CONVERSATION_STATE["history"])

        return {
            "status": "success",
            "active": CONVERSATION_STATE["active"],
            "username": CONVERSATION_STATE["username"],
            "conversation_status": CONVERSATION_STATE["status"],
            "history": history[-10:]
        }