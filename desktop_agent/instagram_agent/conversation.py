from dataclasses import dataclass, field


@dataclass
class ConversationState:
    username: str
    introduced: bool = False
    last_incoming_message: str = ""
    history: list[dict] = field(default_factory=list)


conversations: dict[str, ConversationState] = {}


def normalize_username(username: str) -> str:
    return username.strip().lower()


def get_conversation(
    username: str
) -> ConversationState:

    key = normalize_username(username)

    if key not in conversations:
        conversations[key] = ConversationState(
            username=username
        )

    return conversations[key]


def has_introduced(
    username: str
) -> bool:

    state = get_conversation(username)

    return state.introduced


def mark_introduced(
    username: str
):

    state = get_conversation(username)

    state.introduced = True


def is_duplicate_message(
    username: str,
    message: str
) -> bool:

    state = get_conversation(username)

    cleaned = message.strip()

    if not cleaned:
        return True

    return (
        cleaned ==
        state.last_incoming_message
    )


def save_incoming_message(
    username: str,
    message: str
):

    state = get_conversation(username)

    cleaned = message.strip()

    state.last_incoming_message = cleaned

    state.history.append({
        "role": "person",
        "text": cleaned
    })

    trim_history(state)


def save_nexa_message(
    username: str,
    message: str
):

    state = get_conversation(username)

    cleaned = message.strip()

    state.history.append({
        "role": "nexa",
        "text": cleaned
    })

    trim_history(state)


def get_recent_history(
    username: str,
    limit: int = 12
) -> list[dict]:

    state = get_conversation(username)

    return state.history[-limit:]


def trim_history(
    state: ConversationState,
    limit: int = 24
):

    if len(state.history) > limit:
        state.history = state.history[-limit:]


def format_history(
    username: str
) -> str:

    history = get_recent_history(username)

    if not history:
        return "No previous conversation."

    lines = []

    for item in history:

        role = item.get(
            "role",
            ""
        )

        text = item.get(
            "text",
            ""
        )

        if role == "person":
            speaker = "PERSON"
        else:
            speaker = "NEXA"

        lines.append(
            f"{speaker}: {text}"
        )

    return "\n".join(lines)


def clear_conversation(
    username: str
):

    key = normalize_username(username)

    conversations.pop(
        key,
        None
    )