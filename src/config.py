import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    ENVIRONMENT: str = os.getenv('ENVIRONMENT')
    
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
    
    INITIAL_BALANCE = int(os.getenv('INITIAL_BALANCE'))
    REVENUE =int(os.getenv('REVENUE'))
    DISCS_COUNT_SOLD = int(os.getenv('DISCS_COUNT_SOLD'))
    ALL_ASSETS = int(os.getenv('ALL_ASSETS'))
    
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    
    
config = Config()