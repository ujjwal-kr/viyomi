
import google.generativeai as genai
from dotenv import dotenv_values

config = dotenv_values(".env")

genai.configure(api_key=config["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

response = chat.send_message("Hello")
print(response.candidates[0].content.parts[0].text)