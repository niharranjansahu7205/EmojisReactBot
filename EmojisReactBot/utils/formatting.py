"""
Shared text/markup formatting helpers, mirrored from the
utils/formatting.py pattern used in RegisterBot's other projects.
"""
from telegram.helpers import mention_html


def user_mention(user_id: int, name: str) -> str:
    """Clickable tg://user deep link mention, HTML parse mode."""
    return mention_html(user_id, name)


WELCOME_MESSAGE = (
    "👋 <b>Welcome to EmojisReactBot!</b>\n\n"
    "⚡ Auto react on users' messages\n"
    "🎯 Make your group more fun\n\n"
    "<b>Commands:</b>\n"
    "<code>/reacton @user 😎</code> — set auto reaction (reply to their message)\n"
    "<code>/reactoff @user</code> — remove auto reaction\n"
    "<code>/reactlist</code> — show active reactions\n\n"
    "🚀 Add me to your group, make me admin, and enjoy!"
)

HELP_MESSAGE = (
    "📖 <b>EmojisReactBot — Commands</b>\n\n"
    "<b>/reacton</b> <i>emoji</i> (as a reply)\n"
    "Reply to a user's message with this command to auto-react to everything they send.\n"
    "Example: reply to Rahul's message with <code>/reacton 😂</code>\n\n"
    "<b>/reactoff</b> (as a reply, or with no reply to clear yourself)\n"
    "Reply to a user's message to stop auto-reacting to them.\n"
    "Example: <code>/reactoff</code>\n\n"
    "<b>/reactlist</b>\n"
    "Shows everyone currently set for auto-reactions in this group.\n\n"
    "<b>/clearall</b>\n"
    "Removes all auto-reaction rules in this group (admin only).\n\n"
    "<b>/leaderboard</b>\n"
    "Shows the most-reacted users in this group.\n\n"
    "ℹ️ Max 5 tracked users per group. Only group admins (or the user themself) "
    "can set/remove a reaction rule."
)

NOT_ADMIN_MSG = "❌ Only group admins can do this for other users."
NO_REPLY_MSG = "❌ Please reply to the target user's message with this command."
INVALID_EMOJI_MSG = (
    "❌ Invalid emoji.\nUse a single emoji from Telegram's supported reaction set, e.g. 😂 🔥 ❤️ 👍"
)
BOT_NO_PERMISSION_MSG = (
    "⚠️ I need to be a <b>group admin</b> with permission to add reactions.\n"
    "Please promote me to admin and try again."
)
LIMIT_REACHED_MSG = "❌ Limit reached — max 5 tracked users per group. Remove one with /reactoff first."
USER_NOT_FOUND_MSG = "❌ User not found."
