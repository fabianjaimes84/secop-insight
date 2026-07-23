from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    SECOP_API_URL = os.getenv("SECOP_API_URL")
    TIMEOUT = 30


settings = Settings()
