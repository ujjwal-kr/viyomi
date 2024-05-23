
import google.generativeai as genai
from dotenv import dotenv_values

config = dotenv_values(".env")

genai.configure(api_key=config["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

response = chat.send_message("Hello")
print(response.candidates[0].content.parts[0].text)

from gtts import gTTS
from playsound import playsound

# Define the text to be converted to speech
text = "Hello, world!"

# Create a gTTS object
tts = gTTS(text=text, lang='en')

# Save the audio to a file
tts.save("hello.mp3")

# Play the audio file
playsound("hello.mp3")