import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL") # pyright: ignore[reportAssignmentType]
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))   # 7 days

settings = Settings()
