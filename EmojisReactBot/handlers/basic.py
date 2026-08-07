"""
Basic commands: /start, /help
"""
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from utils.formatting import WELCOME_MESSAGE, HELP_MESSAGE


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode=ParseMode.HTML)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)
