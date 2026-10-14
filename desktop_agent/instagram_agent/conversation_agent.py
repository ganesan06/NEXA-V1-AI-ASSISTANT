from .conversation import (
    format_history,
    get_conversation,
)

from .conversation_prompt import (
    CONVERSATION_INSTRUCTION,
)


def build_conversation_prompt(
    username: str,
    latest_message: str
) -> str:

    state = get_conversation(
        username
    )

    history = format_history(
        username
    )

    if state.introduced:
        introduced = "TRUE"
    else:
        introduced = "FALSE"

    prompt = f"""
{CONVERSATION_INSTRUCTION}

============================================================
CURRENT INSTAGRAM CONVERSATION
============================================================

PERSON USERNAME:

{username}

INTRODUCED:

{introduced}

RECENT CONVERSATION:

{history}

============================================================
LATEST INCOMING MESSAGE
============================================================

{latest_message}

============================================================
YOUR TASK
============================================================

Reply ONLY to the LATEST INCOMING MESSAGE.

Use RECENT CONVERSATION only to understand context.

Generate exactly ONE natural Instagram reply.

Do not include labels.

Do not write "NEXA:".

Do not write "Reply:".

Return only the message.
"""

    return prompt.strip()