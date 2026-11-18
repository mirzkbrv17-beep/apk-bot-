import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    bot_token = os.getenv("BOT_TOKEN", "")
    admin_ids = {int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()}
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/bot.db")
    bot_username = os.getenv("BOT_USERNAME", "").lstrip("@")
    max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "200"))
settings = Settings()
