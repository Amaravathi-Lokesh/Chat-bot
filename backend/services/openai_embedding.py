from google import genai
from config.settings import settings

client = genai.Client(
    api_key=settings.google_api_key
)

def create_embedding(text):

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values