import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env file")

DATABASE_PATH = os.getenv('DATABASE_PATH', './data/bot.db')
os.makedirs(os.path.dirname(DATABASE_PATH) or '.', exist_ok=True)

TIMEZONE = os.getenv('TIMEZONE', 'UTC')

SCHEDULE_HOUR = 9
SCHEDULE_MINUTE = 0
