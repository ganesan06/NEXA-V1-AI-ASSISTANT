from collections.abc import Callable

from .conversation import (
    has_introduced,
    is_duplicate_message,
    mark_introduced,
    save_incoming_message,
    save_nexa_message,
)

from .conversation_agent import (
    build_conversation_prompt,
)


def clean_reply(
    reply: str
) -> str:

    if not reply:
        return ""

    reply = reply.strip()

    prefixes = [
        "NEXA:",
        "Reply:",
        "Response:",
        "Assistant:",
    ]

    for prefix in prefixes:

        if reply.lower().startswith(
            prefix.lower()
        ):

            reply = reply[
                len(prefix):
            ].strip()

    return reply


def process_instagram_message(
    username: str,
    incoming_message: str,
    generate_reply: Callable[[str], str],
    send_message: Callable[[str], None],
):

    username = (
        username or ""
    ).strip()

    incoming_message = (
        incoming_message or ""
    ).strip()


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not username:

        print(
            "[NEXA INSTAGRAM] "
            "Username missing."
        )

        return None


    if not incoming_message:

        print(
            "[NEXA INSTAGRAM] "
            "Incoming message empty."
        )

        return None


    # -----------------------------------------------------
    # DUPLICATE PROTECTION
    # -----------------------------------------------------

    if is_duplicate_message(
        username,
        incoming_message
    ):

        print(
            "[NEXA INSTAGRAM] "
            "Duplicate ignored:"
        )

        print(
            incoming_message
        )

        return None


    # -----------------------------------------------------
    # SAVE REAL INCOMING MESSAGE
    # -----------------------------------------------------

    save_incoming_message(
        username,
        incoming_message
    )


    print()
    print("=" * 55)
    print("[INSTAGRAM INCOMING]")
    print("Person:", username)
    print("Message:", incoming_message)
    print("=" * 55)


    # -----------------------------------------------------
    # BUILD CLEAN MODEL PROMPT
    # -----------------------------------------------------

    prompt = (
        build_conversation_prompt(
            username,
            incoming_message
        )
    )


    # -----------------------------------------------------
    # GENERATE
    # -----------------------------------------------------

    try:

        reply = generate_reply(
            prompt
        )

    except Exception as error:

        print()
        print(
            "[NEXA CONVERSATION ERROR]"
        )

        print(
            type(error).__name__
        )

        print(error)

        return None


    # -----------------------------------------------------
    # CLEAN OUTPUT
    # -----------------------------------------------------

    reply = clean_reply(
        reply
    )


    if not reply:

        print(
            "[NEXA INSTAGRAM] "
            "Empty model response."
        )

        return None


    # -----------------------------------------------------
    # SEND ONE MESSAGE
    # -----------------------------------------------------

    try:

        send_message(
            reply
        )

    except Exception as error:

        print()
        print(
            "[INSTAGRAM SEND ERROR]"
        )

        print(
            type(error).__name__
        )

        print(error)

        return None


    # -----------------------------------------------------
    # SAVE NEXA RESPONSE
    # -----------------------------------------------------

    save_nexa_message(
        username,
        reply
    )


    # -----------------------------------------------------
    # INTRODUCTION COMPLETE
    # -----------------------------------------------------

    if not has_introduced(
        username
    ):

        mark_introduced(
            username
        )


    print()
    print("=" * 55)
    print("[NEXA INSTAGRAM REPLY]")
    print(reply)
    print("=" * 55)
    print()


    return reply