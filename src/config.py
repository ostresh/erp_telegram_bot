import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    DB_CONFIG = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT")),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }
    
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    OWNER_ID = int(os.getenv('OWNER_ID', '0'))
    PROXY_URL = os.getenv('PROXY_URL')
    
    
config = Config()