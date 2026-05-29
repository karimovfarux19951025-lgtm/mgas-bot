import aiosqlite
from datetime import datetime

DB_PATH = "mgas.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                full_name TEXT,
                phone TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                telegram_id INTEGER,
                complaint_type TEXT,
                location_text TEXT,
                latitude REAL,
                longitude REAL,
                description TEXT,
                photo_id TEXT,
                status TEXT DEFAULT 'yangi',
                admin_comment TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        await db.commit()

async def save_user(telegram_id, full_name, phone=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users (telegram_id, full_name, phone, created_at)
            VALUES (?, ?, ?, ?)
        """, (telegram_id, full_name, phone, datetime.now().strftime("%d.%m.%Y %H:%M")))
        await db.commit()

async def save_complaint(telegram_id, complaint_type, location_text, lat, lon, description, photo_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO complaints (telegram_id, complaint_type, location_text, latitude, longitude, description, photo_id, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'yangi', ?, ?)
        """, (telegram_id, complaint_type, location_text, lat, lon, description, photo_id,
              datetime.now().strftime("%d.%m.%Y %H:%M"), datetime.now().strftime("%d.%m.%Y %H:%M")))
        await db.commit()
        return cursor.lastrowid

async def get_user_complaints(telegram_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM complaints WHERE telegram_id = ? ORDER BY id DESC
        """, (telegram_id,))
        return await cursor.fetchall()

async def get_complaint_by_id(complaint_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
        return await cursor.fetchone()

async def get_all_complaints(status=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status:
            cursor = await db.execute("SELECT * FROM complaints WHERE status = ? ORDER BY id DESC", (status,))
        else:
            cursor = await db.execute("SELECT * FROM complaints ORDER BY id DESC")
        return await cursor.fetchall()

async def update_complaint_status(complaint_id, status, admin_comment=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE complaints SET status = ?, admin_comment = ?, updated_at = ?
            WHERE id = ?
        """, (status, admin_comment, datetime.now().strftime("%d.%m.%Y %H:%M"), complaint_id))
        await db.commit()

async def get_statistics():
    async with aiosqlite.connect(DB_PATH) as db:
        stats = {}
        cursor = await db.execute("SELECT COUNT(*) FROM complaints")
        stats['total'] = (await cursor.fetchone())[0]
        cursor = await db.execute("SELECT COUNT(*) FROM complaints WHERE status = 'yangi'")
        stats['yangi'] = (await cursor.fetchone())[0]
        cursor = await db.execute("SELECT COUNT(*) FROM complaints WHERE status = 'jarayonda'")
        stats['jarayonda'] = (await cursor.fetchone())[0]
        cursor = await db.execute("SELECT COUNT(*) FROM complaints WHERE status = 'bajarildi'")
        stats['bajarildi'] = (await cursor.fetchone())[0]
        cursor = await db.execute("SELECT COUNT(*) FROM complaints WHERE status = 'qabul_qilindi'")
        stats['qabul_qilindi'] = (await cursor.fetchone())[0]
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        stats['users'] = (await cursor.fetchone())[0]
        return stats
