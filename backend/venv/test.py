import fitz

pdf = fitz.open("C:\\Users\\amara\\OneDrive\\Desktop\\fastapi-chatbot\\backend\\venv\\upload\\full_cloud_computing_conversation_notes.pdf")

text = ""

for page in pdf:
    text += page.get_text()

print(text[:1000])