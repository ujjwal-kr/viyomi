import pyttsx3

import google.generativeai as genai
from dotenv import dotenv_values
from flask import Flask, jsonify
from flask_cors import CORS
import threading
from flask import request

config = dotenv_values(".env")

speaker = pyttsx3.init()
voices = speaker.getProperty('voices')
speaker.setProperty('voice', voices[1].id)
speaker.setProperty('rate', 160)
speaker.say("Hello world, I am Vyomee")
speaker.runAndWait()

genai.configure(api_key=config["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

app = Flask(__name__)
CORS(app)

def start_flask_server():
    app.run()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask_server)
    flask_thread.start()

with open("prompt.txt") as f:
    prompt = f.read()

chat.send_message(prompt)

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()
    response = chat.send_message(data["message"])
    speaker.say(response.candidates[0].content.parts[0].text)
    speaker.runAndWait()
    return jsonify({"message": 'done'})