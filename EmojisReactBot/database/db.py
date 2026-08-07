"""
SQLite persistence layer for EmojisReactBot.
All calls run through asyncio.to_thread-style aiosqlite connections
so the bot's event loop never blocks on disk I/O.
"""
import time
import aiosqlite
from contextlib import asynccontextmanager

from config import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS reactions (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    username TEXT,
    emoji TEXT NOT NULL,
    added_by INTEGER,
    created_at INTEGER NOT NULL,
    PRIMARY KEY (chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS stats (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    react_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (chat_id, user_id)
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.commit()


@asynccontextmanager
async def get_conn():
    conn = await aiosqlite.connect(DB_PATH)
    try:
        yield conn
    finally:
        await conn.close()


# ---------- Reaction rules ----------

async def add_reaction_rule(chat_id: int, user_id: int, username: str, emoji: str, added_by: int) -> bool:
    """Returns False if the group already has MAX_TRACKED_USERS_PER_GROUP entries
    (and this user isn't already one of them)."""
    from config import MAX_TRACKED_USERS_PER_GROUP

    async with get_conn() as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM reactions WHERE chat_id = ? AND user_id != ?",
            (chat_id, user_id),
        )
        (count,) = await cur.fetchone()
        if count >= MAX_TRACKED_USERS_PER_GROUP:
            return False

        await db.execute(
            """
            INSERT INTO reactions (chat_id, user_id, username, emoji, added_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET
                emoji = excluded.emoji,
                username = excluded.username,
                added_by = excluded.added_by
            """,
            (chat_id, user_id, username, emoji, added_by, int(time.time())),
        )
        await db.commit()
        return True


async def remove_reaction_rule(chat_id: int, user_id: int) -> bool:
    async with get_conn() as db:
        cur = await db.execute(
            "DELETE FROM reactions WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)
        )
        await db.commit()
        return cur.rowcount > 0


async def get_reaction_emoji(chat_id: int, user_id: int):
    async with get_conn() as db:
        cur = await db.execute(
            "SELECT emoji FROM reactions WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        )
        row = await cur.fetchone()
        return row[0] if row else None


async def list_reactions(chat_id: int):
    async with get_conn() as db:
        cur = await db.execute(
            "SELECT user_id, username, emoji FROM reactions WHERE chat_id = ? ORDER BY created_at",
            (chat_id,),
        )
        return await cur.fetchall()


async def count_reactions(chat_id: int) -> int:
    async with get_conn() as db:
        cur = await db.execute("SELECT COUNT(*) FROM reactions WHERE chat_id = ?", (chat_id,))
        (count,) = await cur.fetchone()
        return count


async def clear_all_reactions(chat_id: int) -> int:
    async with get_conn() as db:
        cur = await db.execute("DELETE FROM reactions WHERE chat_id = ?", (chat_id,))
        await db.commit()
        return cur.rowcount


# ---------- Stats / leaderboard ----------

async def bump_stat(chat_id: int, user_id: int):
    async with get_conn() as db:
        await db.execute(
            """
            INSERT INTO stats (chat_id, user_id, react_count) VALUES (?, ?, 1)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET react_count = react_count + 1
            """,
            (chat_id, user_id),
        )
        await db.commit()


async def get_leaderboard(chat_id: int, limit: int = 10):
    async with get_conn() as db:
        cur = await db.execute(
            """
            SELECT s.user_id, r.username, s.react_count
            FROM stats s
            LEFT JOIN reactions r ON r.chat_id = s.chat_id AND r.user_id = s.user_id
            WHERE s.chat_id = ?
            ORDER BY s.react_count DESC
            LIMIT ?
            """,
            (chat_id, limit),
        )
        return await cur.fetchall()
