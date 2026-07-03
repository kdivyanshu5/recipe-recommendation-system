import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "Recipe Recommendation API"
    VERSION = "1.0.0"

settings = Settings()