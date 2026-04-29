from environs import Env
import os

env = Env()
base_dir = os.path.dirname(os.path.dirname(__file__))
env.read_env(os.path.join(base_dir, ".env"))

BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN = env.int("ADMIN")
DATABASE = env.str("DATABASE")