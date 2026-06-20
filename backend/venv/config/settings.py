import os
from dotenv import load_dotenv
load_dotenv()
class Settings:
    api_key=os.getenv("api")
    openapi_key=os.getenv("openai")
    db_key=os.getenv("DATABASE_URL")
settings = Settings()