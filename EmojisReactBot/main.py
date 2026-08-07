"""
EmojisReactBot — entrypoint.

Run with:
    EMOJIS_REACT_BOT_TOKEN=xxxx python main.py

Optional env vars:
    EMOJIS_REACT_DB_PATH           -> SQLite file path (default: emojis_react.db)
    MAX_TRACKED_USERS              -> per-group cap (default: 5)
    REACTION_COOLDOWN_SECONDS      -> per-user cooldown (default: 1.5)
"""
import asyncio
import logging
import sys

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from database.db import init_db
from handlers.basic import start_cmd, help_cmd
from handlers.reactions import (
    reacton_cmd, reactoff_cmd, reactlist_cmd, clearall_cmd, leaderboard_cmd,
)
from handlers.autoreact import auto_react_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("EmojisReactBot")


async def _post_init(application: Application):
    await init_db()
    logger.info("Database initialized.")
    bot_info = await application.bot.get_me()
    logger.info("Bot started as @%s", bot_info.username)


def build_application() -> Application:
    if not BOT_TOKEN:
        logger.error("EMOJIS_REACT_BOT_TOKEN environment variable is not set.")
        sys.exit(1)

    application = ApplicationBuilder().token(BOT_TOKEN).post_init(_post_init).build()

    # Commands
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("reacton", reacton_cmd))
    application.add_handler(CommandHandler("reactoff", reactoff_cmd))
    application.add_handler(CommandHandler("reactlist", reactlist_cmd))
    application.add_handler(CommandHandler("clearall", clearall_cmd))
    application.add_handler(CommandHandler("leaderboard", leaderboard_cmd))

    # Auto-react listener: runs on every non-command group message
    application.add_handler(
        MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, auto_react_handler)
    )

    return application


def main():
    application = build_application()
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
