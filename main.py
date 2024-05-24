#!/usr/bin/python
import google.generativeai as genai
from dotenv import dotenv_values
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import signal
import sys
import subprocess
import time
import os

config = dotenv_values(".env")

lock = 0
i = 0

def has_internet_connection():
    try:
        subprocess.check_call(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

# Wait until an internet connection is available
while not has_internet_connection():
    print("Waiting for internet connection...")
    time.sleep(5)

subprocess.run(["flite", "-voice", "cmu_us_slt.flitevox", "-t", "\"Hello world, I am Veeyomee\""])
subprocess.Popen(["ssh", "-R", "viyomi-proxy.serveo.net:80:localhost:5000", "serveo.net", "&"])

# Configure generative AI model
genai.configure(api_key=config["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# Initialize Flask app
app = Flask(__name__)
CORS(app)

def init_prompt():
    with open("prompt.txt") as f:
        prompt = f.read()

    chat.send_message(prompt)
    print("Initial prompt sent")

@app.route("/ping", methods=["GET"])
def ping_endpoint():
    return jsonify({"message": "pong"})

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    global lock
    global i
    data = request.get_json()
    pin = data['pin']
    if pin == config["PASSKEY"]:
        if lock == 1:
            return jsonify({"message": "bruh"})
        lock = 1
        response = chat.send_message(data["message"])
        i = i + 1
        if i % 5 == 0:
            init_prompt()
        print(i)
        r = response.candidates[0].content.parts[0].text.replace("*", "")
        r.replace("\n", "\n.")
        print(r)
        subprocess.run(["flite", "-voice", "cmu_us_slt.flitevox", "-t", r])
        lock = 0
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

    init_prompt()

    # Wait for the shutdown signal
    shutdown_event.wait()
