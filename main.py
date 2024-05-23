#!/usr/bin/python
import pyttsx3
import google.generativeai as genai
from dotenv import dotenv_values
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import signal
import sys
import subprocess

config = dotenv_values(".env")

# Initialize text-to-speech engine
speaker = pyttsx3.init()
voices = speaker.getProperty('voices')
speaker.setProperty('rate', 160)
speaker.setProperty('voice', 'english_rp+f2')
speaker.say("Hello world, I am Vyomee")
speaker.runAndWait()

subprocess.Popen(["ssh", "-R", "viyomi-proxy.serveo.net:80:localhost:5000", "serveo.net", "&"])

# Configure generative AI model
genai.configure(api_key=config["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route("/ping", methods=["GET"])
def ping_endpoint():
    return jsonify({"message": "pong"})

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()
    pin = data['pin']
    if pin == "00000":
        response = chat.send_message(data["message"])
        speaker.say(response.candidates[0].content.parts[0].text)
        speaker.runAndWait()
        return jsonify({"message": 'done'})
    return jsonify({"message": "done"})

def start_flask_server():
    app.run()

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print('Shutting down...')
    shutdown_event.set()
    sys.exit(0)

if __name__ == "__main__":
    # Create an event to keep the main thread alive
    shutdown_event = threading.Event()

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=start_flask_server)
    flask_thread.start()

    with open("prompt.txt") as f:
        prompt = f.read()

    chat.send_message(prompt)
    print("Initial prompt sent")

    # Wait for the shutdown signal
    shutdown_event.wait()
