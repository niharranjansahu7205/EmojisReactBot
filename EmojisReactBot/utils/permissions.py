"""
Permission helpers: group-admin checks and bot's own reaction capability.
"""
import logging
from telegram import Chat, ChatMember
from telegram.error import TelegramError
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

_ADMIN_STATUSES = {ChatMember.ADMINISTRATOR, ChatMember.OWNER}


async def is_user_admin_or_self(chat_id: int, user_id: int, target_user_id: int,
                                  context: ContextTypes.DEFAULT_TYPE) -> bool:
    """/reacton can be used by a group admin OR by the command sender acting on
    themselves (sender == target). Returns True if allowed."""
    if user_id == target_user_id:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in _ADMIN_STATUSES
    except TelegramError as e:
        logger.warning("Admin check failed for chat=%s user=%s: %s", chat_id, user_id, e)
        return False


async def bot_can_react(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks the bot is an admin in the chat with can_post_messages/reaction rights.
    Telegram's Bot API doesn't expose a discrete 'can_add_reactions' ChatMember flag
    at the time of writing, so we verify the bot is an admin, which is required for
    setMessageReaction to work reliably in supergroups."""
    try:
        me = await context.bot.get_me()
        member = await context.bot.get_chat_member(chat_id, me.id)
        return member.status in _ADMIN_STATUSES
    except TelegramError as e:
        logger.warning("Bot permission check failed for chat=%s: %s", chat_id, e)
        return False
