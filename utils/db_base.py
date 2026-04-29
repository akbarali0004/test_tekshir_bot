import aiosqlite as sq
# from data.config import DATABASE


class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    async def db_start(self):
        async with sq.connect(self.db_path) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS users(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            full_name TEXT NOT NULL,
                            tg_id INTEGER NOT NULL UNIQUE,
                            created_at DATETIME DEFAULT (datetime('now', '+5 hours')),
                            role TEXT DEFAULT 'user'
                            );""")
            
            await db.execute("""CREATE TABLE IF NOT EXISTS tests(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            answers TEXT NOT NULL,
                            status TEXT DEFAULT 'waiting', --active, close
                            author_id INTEGER,
                            created_at DATETIME DEFAULT (datetime('now', '+5 hours')),
                            FOREIGN KEY (author_id) REFERENCES users (tg_id)
                            );""")
            
            await db.execute("""CREATE TABLE IF NOT EXISTS results(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            test_id INTEGER,
                            result TEXT NOT NULL, -- 16/20
                            percentage REAL NOT NULL,
                            created_at TEXT DEFAULT (datetime('now', '+5 hours')),
                            FOREIGN KEY (user_id) REFERENCES users (tg_id),
                            FOREIGN KEY (test_id) REFERENCES tests (id)
                            );""")
            
            await db.execute("""CREATE TABLE IF NOT EXISTS channels(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT,
                            channel_id INTEGER UNIQUE NOT NULL,
                            invite_link TEXT
                            );""")

    # 1. Userlarni boshqarish
    async def add_user(self, tg_id: int, full_name: str | None, role='user'):
        async with sq.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (tg_id, full_name, role) VALUES (?, ?, ?)",
                (tg_id, full_name, role)
            )
            await db.commit()

    async def update_fullname(self, tg_id: int, full_name: str):
        async with sq.connect(self.db_path) as db:
            await db.execute("UPDATE users SET full_name = ? WHERE tg_id = ?", (full_name, tg_id))
            await db.commit()

    async def get_user(self, tg_id):
        async with sq.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)) as cursor:
                return await cursor.fetchone()


    # 2. Adminlarni boshqarish
    async def make_admin(self, tg_id: int):
        async with sq.connect(self.db_path) as db:
            await db.execute("UPDATE users SET role = 'admin' WHERE tg_id = ?", (tg_id,))
            await db.commit()

    async def get_admin(self, tg_id):
        async with sq.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE tg_id = ? AND role IN ('owner', 'admin')", (tg_id,)) as cursor:
                return await cursor.fetchone()

    async def get_admins(self):
        async with sq.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE role IN ('owner', 'admin')") as cursor:
                return await cursor.fetchall()
            
    async def remove_admin(self, tg_id: int):
        async with sq.connect(self.db_path) as db:
            await db.execute("UPDATE users SET role = 'user' WHERE tg_id = ?", (tg_id,))
            await db.commit()


    # 3. Testlarni boshqarish
    async def add_test(self, title:str, answers: str, author_id: int):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO tests (title, answers, author_id) 
                VALUES (?, ?, ?)
            """, (title, answers, author_id))
            await db.commit()
            return cursor.lastrowid
        
    async def get_test(self, test_code:int):
        async with sq.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM tests WHERE id = ?", (test_code,)) as cursor:
                return await cursor.fetchone()
            
    async def test_update_status(self, test_code: int, status:str):
        async with sq.connect(self.db_path) as db:
            await db.execute("UPDATE tests SET status = ? WHERE id = ?", (status, test_code,))
            await db.commit()

                
    # 4. Natijani boshqarish
    async def save_result(self, user_id: int, test_id: int, result: str, percentage: float):
        async with sq.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO results (user_id, test_id, result, percentage) 
                VALUES (?, ?, ?, ?)
            """, (user_id, test_id, result, percentage))
            await db.commit()
    
    async def get_results(self, test_id: int):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT users.full_name, results.result, results.percentage, results.created_at
                FROM results
                JOIN users ON results.user_id = users.tg_id
                WHERE results.test_id = ?
                ORDER BY results.percentage DESC
            """, (test_id,))
            
            return await cursor.fetchall()
        
    async def del_results(self, test_id: int):
        async with sq.connect(self.db_path) as db:
            await db.execute("""DELETE FROM results WHERE id = ?""", (test_id,))
            return await db.commit()


    # 5. Kanallarni boshqarish
    async def add_channel(self, title:str | None, channel_id: int, invite_link: str | None):
        async with sq.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO channels (channel_id, invite_link) VALUES (?, ?)", 
                             (channel_id, invite_link))
            await db.commit()

    async def get_channel(self, channel_id:int):
        async with sq.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM channels WHERE channel_id = ?", (channel_id, )) as cursor:
                return await cursor.fetchone()
            
    async def get_channels(self):
        async with sq.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM channels") as cursor:
                return await cursor.fetchall()

    async def delete_channel(self, channel_id: int):
        async with sq.connect(self.db_path) as db:
            await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
            await db.commit()

    
    # Foydalanuvchi bir marta topshirishini tekshirish
    async def check_user_finished(self, user_id, test_id):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute("SELECT id FROM results WHERE user_id = ? AND test_id = ?", (user_id, test_id))
            return await cursor.fetchone()

    # Foydalanuvchining barcha natijalarini olish (JOIN orqali)
    async def get_user_results(self, user_id):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT tests.title, results.result, results.percentage, results.created_at
                FROM results
                JOIN tests ON results.test_id = tests.id
                WHERE results.user_id = ?
                ORDER BY results.id DESC
            """, (user_id,))
            return await cursor.fetchall()

    # Topshirilgan testlar soni
    async def get_user_results_count(self, user_id):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM results WHERE user_id = ?", (user_id,))
            res = await cursor.fetchone()
            return res[0] if res else 0
        
    async def add_result(self, user_id: int, test_id: int, result: str, percentage: float):
        async with sq.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO results (user_id, test_id, result, percentage)
                VALUES (?, ?, ?, ?)
            """, (user_id, test_id, result, percentage))
            await db.commit()

        
    async def count_users(self):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            res = await cursor.fetchone()
            return res[0]

    async def get_admin_tests(self, admin_id):
        async with sq.connect(self.db_path) as db:
            # author_id bo'yicha testlarni olish
            cursor = await db.execute("SELECT * FROM tests WHERE author_id = ? ORDER BY id DESC LIMIT 10", (admin_id,))
            return await cursor.fetchall()

    async def get_all_users(self):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute("SELECT tg_id FROM users")
            return await cursor.fetchall()
        

    async def get_admin_tests_paginated(self, admin_id, limit, offset):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM tests WHERE author_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
                (admin_id, limit, offset)
            )
            return await cursor.fetchall()

    async def get_admin_tests_count(self, admin_id):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM tests WHERE author_id = ?", (admin_id,))
            res = await cursor.fetchone()
            return res[0] if res else 0
        
    
    async def count_all_tests(self):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM tests")
            res = await cursor.fetchone()
            return res[0] if res else 0

    async def count_admins(self):
        async with sq.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users WHERE role IN ('owner', 'admin')")
            res = await cursor.fetchone()
            return res[0] if res else 0

    async def count_channels(self):
        async with sq.connect(self.db_path) as db:
            # Majburiy obuna kanallari jadvali nomi 'channels' deb faraz qilamiz
            cursor = await db.execute("SELECT COUNT(*) FROM channels")
            res = await cursor.fetchone()
            return res[0] if res else 0
        
    
    async def update_channel_link(self, channel_id: int, link: str):
        async with sq.connect(self.db_path) as db:
            await db.execute(
                "UPDATE channels SET invite_link = ? WHERE channel_id = ?",
                (link, channel_id)
            )
            await db.commit()