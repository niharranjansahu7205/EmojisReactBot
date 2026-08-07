"""
In-memory per-(chat, user) cooldown tracker so the bot doesn't hammer the
Telegram Reaction API when a tracked user sends messages rapidly.
"""
import time
from config import REACTION_COOLDOWN_SECONDS

_last_reacted: dict[tuple[int, int], float] = {}


def is_on_cooldown(chat_id: int, user_id: int) -> bool:
    key = (chat_id, user_id)
    last = _last_reacted.get(key, 0.0)
    return (time.monotonic() - last) < REACTION_COOLDOWN_SECONDS


def mark_reacted(chat_id: int, user_id: int):
    _last_reacted[(chat_id, user_id)] = time.monotonic()
