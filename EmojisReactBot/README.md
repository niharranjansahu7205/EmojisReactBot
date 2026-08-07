# EmojisReactBot

A Telegram bot that auto-reacts with a chosen emoji to a specific user's messages in a group.

## Setup

```bash
pip install -r requirements.txt
```

**Set your bot token** — two ways:

1. **`.env` file (recommended)**: copy `.env.example` to `.env` and fill in your token:
   ```
   cp .env.example .env
   # then edit .env and set EMOJIS_REACT_BOT_TOKEN=your_token_here
   ```
2. **Or export directly in your shell** (only lasts for that terminal session):
   ```bash
   export EMOJIS_REACT_BOT_TOKEN="your_bot_token_from_BotFather"
   ```

Get your token by messaging [@BotFather](https://t.me/BotFather) on Telegram → `/newbot`.

Then run:
```bash
python main.py
```

Optional env vars:
- `EMOJIS_REACT_DB_PATH` — SQLite file path (default: `emojis_react.db`). Set this to a persistent volume path in production so data survives redeploys.
- `MAX_TRACKED_USERS` — per-group cap (default: `5`)
- `REACTION_COOLDOWN_SECONDS` — per-user cooldown between auto-reactions (default: `1.5`)

## Bot setup on Telegram

1. Add the bot to your group.
2. Promote it to **Admin** (it needs admin rights for `setMessageReaction` to work reliably in supergroups).
3. Use `/reacton` by **replying** to the target user's message with the command + emoji, e.g.:
   ```
   (reply to Rahul's message)
   /reacton 😂
   ```

## Why reply-based instead of `/reacton @username`?

Telegram's Bot API has no method to resolve an arbitrary `@username` to a numeric `user_id` unless
that user has previously started the bot directly. There is no "look up any group member by
username" endpoint available to bots. So instead of a fragile/broken `@username` parser, the bot
uses the **reply-to-message** pattern — the same approach used by essentially all moderation and
utility bots on Telegram (ban, warn, promote commands all work this way too). It's 100% reliable
regardless of whether the bot has seen that user's username before.

## Commands

| Command | Description |
|---|---|
| `/start` | Welcome message |
| `/help` | Full command reference |
| `/reacton <emoji>` | Reply to a user's message to set auto-reaction (admin or self only) |
| `/reactoff` | Reply to remove a user's reaction rule (no reply = clears your own) |
| `/reactlist` | List active reaction rules in the group |
| `/clearall` | Admin-only: wipe all reaction rules in the group |
| `/leaderboard` | Most-reacted users in the group |

## Project structure

```
emojis_react_bot/
├── main.py                 # Entrypoint, wires handlers
├── config.py                # Env-based config, allowed emoji set
├── database/
│   └── db.py                 # SQLite persistence (reactions + stats)
├── handlers/
│   ├── basic.py               # /start, /help
│   ├── reactions.py           # /reacton, /reactoff, /reactlist, /clearall, /leaderboard
│   └── autoreact.py           # Core listener: reacts to tracked users' messages
└── utils/
    ├── permissions.py         # Admin / bot-permission checks
    ├── formatting.py          # Message templates, mentions
    └── cooldown.py            # In-memory per-user reaction cooldown
```

## Notes on the emoji set

Telegram restricts **message reactions** (as opposed to regular text emoji) to a fixed
server-side list — arbitrary Unicode emoji are rejected by `setMessageReaction` even if
they're valid emoji elsewhere. `config.ALLOWED_REACTION_EMOJIS` contains a broad, currently-supported
subset (👍 👎 ❤️ 🔥 😂 🎉 😍 🤡 💯 etc.). If Telegram adds/removes reaction emoji in the future,
update that set.

## Known limitations (by design)

- **Custom/animated emoji reactions** require the bot to have Telegram Premium-linked
  privileges (`ReactionTypeCustomEmoji`) and are only usable in chats that allow custom emoji
  reactions. This isn't wired up by default since it needs extra chat-level permission checks;
  the `ReactionTypeEmoji` (standard set) path is fully implemented and works everywhere.
- Multiple emojis per user isn't stored as a list currently (schema stores one emoji per
  user per chat) — extending `reactions.emoji` to a JSON array and updating `set_message_reaction`
  to pass multiple `ReactionTypeEmoji` objects is a small follow-up if you want it.
