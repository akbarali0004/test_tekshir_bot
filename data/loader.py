from .config import ADMIN, DATABASE
from utils.db_base import Database

db = Database(DATABASE)

ADMINS = []

async def update_admins_cache():
    await db.add_user(ADMIN, "Owner", "owner")
    
    global ADMINS
    admins_from_db = await db.get_admins()
    ADMINS = [admin[2] for admin in admins_from_db]


CHANNELS = []   

# Bot ishga tushganda yoki kanallar o'zgarganda chaqiriladi
async def update_channels_cache():
    global CHANNELS
    CHANNELS = await db.get_channels()