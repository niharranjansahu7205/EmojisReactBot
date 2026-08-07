"""
Core auto-reaction logic: fires on every group message, checks whether the
sender has an active reaction rule, and reacts via Telegram's Reaction API
(Bot.set_message_reaction), respecting a per-user cooldown.
"""
import logging
from telegram import Update, ReactionTypeEmoji
from telegram.error import TelegramError
from telegram.constants import ChatType
from telegram.ext import ContextTypes

from database import db
from utils.cooldown import is_on_cooldown, mark_reacted

logger = logging.getLogger(__name__)


async def auto_react_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if message is None or chat is None or user is None:
        return
    if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return
    if user.is_bot:
        return

    emoji = await db.get_reaction_emoji(chat.id, user.id)
    if not emoji:
        return

    if is_on_cooldown(chat.id, user.id):
        return

    try:
        await context.bot.set_message_reaction(
            chat_id=chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=emoji)],
            is_big=False,
        )
        mark_reacted(chat.id, user.id)
        await db.bump_stat(chat.id, user.id)
    except TelegramError as e:
        # Common cause: bot lost admin/reaction permission. Log and move on —
        # we don't want to spam the group with error messages on every message.
        logger.warning(
            "Failed to react in chat=%s to message=%s: %s", chat.id, message.message_id, e
        )
