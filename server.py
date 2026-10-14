import asyncio
import uuid
from queue import Queue

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from desktop_agent import root_agent


# =========================================================
# SETTINGS
# =========================================================

APP_NAME = "nexa"
USER_ID = "local_user"
SESSION_ID = str(uuid.uuid4())


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="NEXA Desktop AI",
    version="4.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


# =========================================================
# ADK
# =========================================================

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

session_created = False

agent_lock = asyncio.Lock()


# =========================================================
# CHAT HISTORY
# =========================================================

chat_history = {}


# =========================================================
# FLOATING WINDOWS
# =========================================================

floating_chats = {}

floating_window_queue = Queue()


# =========================================================
# MODELS
# =========================================================

class ChatRequest(BaseModel):
    message: str
    chat_id: str | None = None


class CreateChatRequest(BaseModel):
    chat_id: str | None = None


# =========================================================
# NORMALIZE AGENT
# =========================================================

def normalize_agent_name(agent_name):

    if not agent_name:
        return "nexa"

    name = str(agent_name).lower()

    if "instagram" in name:
        return "instagram"

    if "mail" in name:
        return "mail"

    if "music" in name:
        return "music"

    if "messaging" in name:
        return "messaging"

    if "whatsapp" in name:
        return "messaging"

    if "app" in name:
        return "app"

    return "nexa"


# =========================================================
# CREATE CHAT
# =========================================================

def create_chat_record(chat_id=None):

    if not chat_id:
        chat_id = (
            "chat_" +
            str(uuid.uuid4())
        )

    if chat_id not in chat_history:

        chat_history[chat_id] = {
            "id": chat_id,
            "title": "New Chat",
            "turns": []
        }

    return chat_history[chat_id]


# =========================================================
# UPDATE CHAT TITLE
# =========================================================

def update_chat_title(chat):

    if chat["title"] != "New Chat":
        return

    if not chat["turns"]:
        return

    prompt = (
        chat["turns"][0]
        .get("prompt", "")
        .strip()
    )

    if not prompt:
        return

    if len(prompt) > 35:
        prompt = prompt[:35] + "..."

    chat["title"] = prompt


# =========================================================
# ADD TURN
# =========================================================

def add_turn(chat_id, prompt):

    chat = create_chat_record(
        chat_id
    )

    turn = {
        "id":
            "turn_" +
            str(uuid.uuid4()),

        "prompt":
            prompt,

        "response":
            ""
    }

    chat["turns"].append(
        turn
    )

    update_chat_title(
        chat
    )

    return turn


# =========================================================
# UPDATE RESPONSE
# =========================================================

def update_turn_response(
    chat_id,
    turn_id,
    response
):

    chat = chat_history.get(
        chat_id
    )

    if not chat:
        return

    for turn in chat["turns"]:

        if turn["id"] == turn_id:

            turn["response"] = response

            return


# =========================================================
# CREATE ADK SESSION
# =========================================================

async def ensure_session():

    global session_created

    if session_created:
        return

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    session_created = True

    print()
    print("=" * 60)
    print("NEXA SESSION CREATED")
    print("SESSION:", SESSION_ID)
    print("=" * 60)
    print()


# =========================================================
# RUN AGENT
# =========================================================

async def run_agent(message):

    await ensure_session()

    user_message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=message
            )
        ]
    )

    final_text = ""

    active_agent = (
        "desktop_manager"
    )

    async with agent_lock:

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=user_message
        ):

            author = getattr(
                event,
                "author",
                None
            )

            if author:

                active_agent = author

                print(
                    "[ACTIVE AGENT]",
                    author
                )

            content = getattr(
                event,
                "content",
                None
            )

            if not content:
                continue

            parts = getattr(
                content,
                "parts",
                None
            )

            if not parts:
                continue

            for part in parts:

                text = getattr(
                    part,
                    "text",
                    None
                )

                if not text:
                    continue

                text = text.strip()

                if not text:
                    continue

                print()
                print(
                    f"[{author or 'agent'}]"
                )
                print(text)

                final_text = text

    if not final_text:

        final_text = (
            "The task completed, but "
            "no text response was returned."
        )

    return (
        final_text,
        active_agent
    )


# =========================================================
# MAIN PAGE
# =========================================================

@app.get("/")
async def home():

    return FileResponse(
        "frontend/index.html"
    )


# =========================================================
# FLOATING PAGE
# =========================================================

@app.get("/floating")
async def floating_page():

    return FileResponse(
        "frontend/floating.html"
    )


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
async def health():

    return {
        "status": "online",
        "application": "NEXA"
    }


# =========================================================
# CREATE HISTORY
# =========================================================

@app.post("/history/create")
async def create_history(
    request: CreateChatRequest
):

    chat = create_chat_record(
        request.chat_id
    )

    return chat


# =========================================================
# GET HISTORY
# =========================================================

@app.get("/history")
async def get_history():

    return {
        "chats":
            list(
                chat_history.values()
            )
    }


# =========================================================
# GET ONE CHAT
# =========================================================

@app.get("/history/{chat_id}")
async def get_chat(
    chat_id: str
):

    chat = chat_history.get(
        chat_id
    )

    if chat:
        return chat

    return {
        "id": chat_id,
        "title": "New Chat",
        "turns": []
    }


# =========================================================
# DELETE CHAT
# =========================================================

@app.delete("/history/{chat_id}")
async def delete_chat(
    chat_id: str
):

    chat_history.pop(
        chat_id,
        None
    )

    return {
        "status": "deleted"
    }


# =========================================================
# FLOAT CHAT
#
# IMPORTANT:
# We intentionally use Request here instead of a strict
# Pydantic FloatRequest model.
#
# This prevents old/new frontend field mismatches from
# automatically becoming FastAPI 422 errors.
# =========================================================

@app.post("/float-chat")
async def float_chat(
    request: Request
):

    try:

        data = await request.json()

    except Exception as error:

        print()
        print("[FLOAT ERROR]")
        print("Invalid JSON")
        print(error)

        return {
            "status": "error",
            "message": "Invalid JSON request."
        }


    print()
    print("=" * 60)
    print("[FLOAT RAW DATA]")
    print(data)
    print("=" * 60)


    # -----------------------------------------------------
    # SUPPORT DIFFERENT FIELD NAMES
    # -----------------------------------------------------

    chat_id = (
        data.get("chat_id")
        or
        data.get("chatId")
        or
        data.get("conversation_id")
        or
        data.get("conversationId")
    )


    prompt = (
        data.get("prompt")
        or
        data.get("message")
        or
        data.get("user_message")
        or
        data.get("userMessage")
        or
        ""
    )


    response_text = (
        data.get("response")
        or
        data.get("result")
        or
        data.get("answer")
        or
        data.get("assistant_response")
        or
        data.get("assistantResponse")
        or
        ""
    )


    # -----------------------------------------------------
    # CHAT ID FALLBACK
    # -----------------------------------------------------

    if not chat_id:

        chat_id = (
            "chat_" +
            str(uuid.uuid4())
        )

        print(
            "[FLOAT] chat_id was missing."
        )

        print(
            "[FLOAT] Created:",
            chat_id
        )


    # -----------------------------------------------------
    # VALIDATE PROMPT
    # -----------------------------------------------------

    if not prompt:

        print(
            "[FLOAT ERROR] "
            "Prompt missing."
        )

        return {
            "status": "error",
            "message":
                "Prompt is missing."
        }


    # -----------------------------------------------------
    # VALIDATE RESPONSE
    # -----------------------------------------------------

    if not response_text:

        print(
            "[FLOAT ERROR] "
            "Response missing."
        )

        return {
            "status": "error",
            "message":
                "Response is missing."
        }


    # -----------------------------------------------------
    # MAKE SURE CHAT EXISTS
    # -----------------------------------------------------

    chat = create_chat_record(
        chat_id
    )


    # -----------------------------------------------------
    # CREATE FLOAT ID
    # -----------------------------------------------------

    floating_id = str(
        uuid.uuid4()
    )


    floating_chats[
        floating_id
    ] = {

        "floating_id":
            floating_id,

        "chat_id":
            chat["id"],

        "prompt":
            str(prompt),

        "response":
            str(response_text)
    }


    # -----------------------------------------------------
    # SEND TO RUN.PY
    # -----------------------------------------------------

    floating_window_queue.put(
        floating_id
    )


    print()
    print("[FLOAT SUCCESS]")
    print(
        "Float ID:",
        floating_id
    )
    print(
        "Chat ID:",
        chat["id"]
    )
    print()


    return {
        "status": "success",
        "floating_id":
            floating_id,
        "chat_id":
            chat["id"]
    }


# =========================================================
# FLOAT DATA
# =========================================================

@app.get(
    "/floating-data/{floating_id}"
)
async def floating_data(
    floating_id: str
):

    data = floating_chats.get(
        floating_id
    )

    if not data:

        return {
            "status": "error",
            "floating_id":
                floating_id,
            "chat_id": "",
            "prompt": "",
            "response":
                "Floating chat not found."
        }

    return data


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
async def chat(
    request: ChatRequest
):

    message = (
        request.message
        .strip()
    )

    if not message:

        return {
            "response":
                "Please enter a message.",
            "agent":
                "nexa",
            "agent_name":
                "desktop_manager",
            "chat_id":
                request.chat_id
        }


    chat_id = (
        request.chat_id
        or
        "chat_" +
        str(uuid.uuid4())
    )


    create_chat_record(
        chat_id
    )


    turn = add_turn(
        chat_id,
        message
    )


    print()
    print("=" * 60)
    print("[USER]")
    print(message)
    print("[CHAT]")
    print(chat_id)
    print("=" * 60)


    try:

        final_text, active_agent = (
            await run_agent(
                message
            )
        )


        update_turn_response(
            chat_id,
            turn["id"],
            final_text
        )


        return {

            "response":
                final_text,

            "agent":
                normalize_agent_name(
                    active_agent
                ),

            "agent_name":
                active_agent,

            "chat_id":
                chat_id,

            "turn_id":
                turn["id"]
        }


    except Exception as error:

        error_text = (
            "NEXA encountered an error: "
            + str(error)
        )


        update_turn_response(
            chat_id,
            turn["id"],
            error_text
        )


        print()
        print("=" * 60)
        print("[NEXA ERROR]")
        print(
            type(error).__name__
        )
        print(error)
        print("=" * 60)
        print()


        return {

            "response":
                error_text,

            "agent":
                "nexa",

            "agent_name":
                "desktop_manager",

            "chat_id":
                chat_id,

            "turn_id":
                turn["id"]
        }