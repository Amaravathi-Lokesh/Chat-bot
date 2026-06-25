import os
from dotenv import load_dotenv
load_dotenv()
class Settings:
    api_key=os.getenv("api")
    openapi_key=os.getenv("openai")
    db_key=os.getenv("DATABASE_URL")
    key=os.getenv("SECRET_KEY")
    google_api_key=os.getenv("googleapi")
settings = Settings()