"""
Reaction rule management: /reacton, /reactoff, /reactlist, /clearall, /leaderboard

IMPORTANT DESIGN NOTE:
Telegram's Bot API has no method to resolve an arbitrary @username to a user_id
unless that user has previously started the bot or is otherwise known to it.
So instead of parsing "@username" out of the command text, these commands work
by REPLY: the admin replies to the target user's message and runs the command.
This is the standard, reliable pattern used by moderation bots.
"""
import logging
from telegram import Update
from telegram.constants import ParseMode, ChatType
from telegram.ext import ContextTypes

from config import ALLOWED_REACTION_EMOJIS
from database import db
from utils.permissions import is_user_admin_or_self, bot_can_react
from utils.formatting import (
    NOT_ADMIN_MSG, NO_REPLY_MSG, INVALID_EMOJI_MSG, BOT_NO_PERMISSION_MSG,
    LIMIT_REACHED_MSG, user_mention,
)

logger = logging.getLogger(__name__)


def _group_only(update: Update) -> bool:
    return update.effective_chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)


async def reacton_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _group_only(update):
        await update.message.reply_text("❌ This command only works in groups.")
        return

    message = update.message
    chat_id = update.effective_chat.id
    sender_id = update.effective_user.id

    if not message.reply_to_message:
        await message.reply_text(NO_REPLY_MSG)
        return

    target_user = message.reply_to_message.from_user
    if target_user is None or target_user.is_bot:
        await message.reply_text("❌ User not found.")
        return

    # Parse emoji from command args
    if not context.args:
        await message.reply_text(INVALID_EMOJI_MSG)
        return
    emoji = context.args[0].strip()
    if emoji not in ALLOWED_REACTION_EMOJIS:
        await message.reply_text(INVALID_EMOJI_MSG)
        return

    # Permission: admin or acting on self
    allowed = await is_user_admin_or_self(chat_id, sender_id, target_user.id, context)
    if not allowed:
        await message.reply_text(NOT_ADMIN_MSG)
        return

    # Bot must be able to react
    if not await bot_can_react(chat_id, context):
        await message.reply_text(BOT_NO_PERMISSION_MSG, parse_mode=ParseMode.HTML)
        return

    username = target_user.username or target_user.first_name
    ok = await db.add_reaction_rule(chat_id, target_user.id, username, emoji, sender_id)
    if not ok:
        await message.reply_text(LIMIT_REACHED_MSG)
        return

    mention = user_mention(target_user.id, username)
    await message.reply_text(
        f"✅ Reaction set for {mention} → {emoji}", parse_mode=ParseMode.HTML
    )


async def reactoff_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _group_only(update):
        await update.message.reply_text("❌ This command only works in groups.")
        return

    message = update.message
    chat_id = update.effective_chat.id
    sender_id = update.effective_user.id

    if message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
    else:
        # No reply → default to clearing the sender's own rule
        target_user = update.effective_user

    allowed = await is_user_admin_or_self(chat_id, sender_id, target_user.id, context)
    if not allowed:
        await message.reply_text(NOT_ADMIN_MSG)
        return

    removed = await db.remove_reaction_rule(chat_id, target_user.id)
    username = target_user.username or target_user.first_name
    mention = user_mention(target_user.id, username)
    if removed:
        await message.reply_text(f"✅ Reaction removed for {mention}", parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(f"ℹ️ {mention} had no active reaction.", parse_mode=ParseMode.HTML)


async def reactlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _group_only(update):
        await update.message.reply_text("❌ This command only works in groups.")
        return

    chat_id = update.effective_chat.id
    rows = await db.list_reactions(chat_id)
    if not rows:
        await update.message.reply_text("ℹ️ No active reactions in this group yet.\nUse /reacton to set one.")
        return

    lines = ["🎯 <b>Active Reactions</b>\n"]
    for user_id, username, emoji in rows:
        mention = user_mention(user_id, username or "user")
        lines.append(f"• {mention} → {emoji}")
    lines.append(f"\n({len(rows)}/5 slots used)")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def clearall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _group_only(update):
        await update.message.reply_text("❌ This command only works in groups.")
        return

    chat_id = update.effective_chat.id
    sender_id = update.effective_user.id

    # Admin-only, no self-exception here since it clears everyone's rules
    try:
        member = await context.bot.get_chat_member(chat_id, sender_id)
        is_admin = member.status in ("administrator", "creator")
    except Exception as e:
        logger.warning("clearall admin check failed: %s", e)
        is_admin = False

    if not is_admin:
        await update.message.reply_text(NOT_ADMIN_MSG)
        return

    count = await db.clear_all_reactions(chat_id)
    await update.message.reply_text(f"🧹 Cleared {count} reaction rule(s) in this group.")


async def leaderboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _group_only(update):
        await update.message.reply_text("❌ This command only works in groups.")
        return

    chat_id = update.effective_chat.id
    rows = await db.get_leaderboard(chat_id)
    if not rows:
        await update.message.reply_text("ℹ️ No reactions given yet in this group.")
        return

    lines = ["🏆 <b>Most Reacted Users</b>\n"]
    medals = ["🥇", "🥈", "🥉"]
    for i, (user_id, username, count) in enumerate(rows):
        prefix = medals[i] if i < 3 else f"{i + 1}."
        mention = user_mention(user_id, username or "user")
        lines.append(f"{prefix} {mention} — {count} reactions")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)
