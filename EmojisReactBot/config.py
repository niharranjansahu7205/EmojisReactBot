"""
Central configuration for EmojisReactBot.
All persistence-critical paths and secrets come from environment variables
so nothing is lost on redeploys/updates.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()  # loads variables from a .env file in the project root, if present
except ImportError:
    pass  # python-dotenv not installed; fall back to real environment variables only

BOT_TOKEN = os.environ.get("EMOJIS_REACT_BOT_TOKEN", "")

# DB path is env-driven (same pattern as CRICKET_ROYALE_DB_PATH) so the
# database survives redeploys / container restarts.
DB_PATH = os.environ.get("EMOJIS_REACT_DB_PATH", "emojis_react.db")

# Business rules
MAX_TRACKED_USERS_PER_GROUP = int(os.environ.get("MAX_TRACKED_USERS", "5"))
REACTION_COOLDOWN_SECONDS = float(os.environ.get("REACTION_COOLDOWN_SECONDS", "1.5"))

# A safe, currently-allowed subset of Telegram's reaction emoji set.
# Telegram restricts message reactions to a fixed server-side list —
# arbitrary emoji are rejected by the Bot API even if Unicode-valid.
ALLOWED_REACTION_EMOJIS = {
    "👍", "👎", "❤️", "🔥", "🥳", "👏", "😁", "🤔", "🤯", "😱",
    "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊️", "🤡",
    "🥱", "🥴", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡",
    "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈",
    "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨",
    "🤝", "✍️", "🤗", "🫡", "🎅", "🎄", "☃️", "💅", "🤪", "🗿",
    "🆒", "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂️",
    "🤷", "🤷‍♀️", "😡",
}
