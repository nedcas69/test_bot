import aiosqlite
import sqlite3


async def init_db():
    async with aiosqlite.connect('users.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')
        await db.commit()


async def save_user_to_db(user_id, name, age):
    async with aiosqlite.connect('users.db') as db:
        await db.execute('INSERT INTO users (id, name, age) VALUES (?, ?, ?)', (user_id, name, age))
        await db.commit()


async def get_users():
    async with aiosqlite.connect('users.db') as db:
        async with db.execute('SELECT * FROM users') as cursor:
            return await cursor.fetchall()


async def get_user(id):
    async with aiosqlite.connect('users.db') as db:
        async with db.execute(f'SELECT * FROM users WHERE id = {id}') as cursor:
            return await cursor.fetchone()


def get_users_sync():
    with sqlite3.connect('users.db') as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
    return users
