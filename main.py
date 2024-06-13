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
import speech_recognition as sr

r = sr.Recognizer()
mic  = sr.Microphone()

config = dotenv_values(".env")

i = 0
lock = 0
mic_state = 0

def has_internet_connection():
    try:
        subprocess.check_call(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def add_spaces_between_uppercase(text):
    words = text.split()
    new_words = []
    for word in words:
        if word.isupper():
            spaced_word = ' '.join(word)
            new_words.append(spaced_word)
        else:
            new_words.append(word)
    return ' '.join(new_words)

def listen_to_mic():
    global i
    global lock
    global mic_state
    while True:
        if mic_state == 1:
            print("Listening...")
            subprocess.run(["flite", "-voice", "cmu_us_slt.flitevox", "-t", "Listening"])
            with mic as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
            print("Processing now...")
            try:
                data = r.recognize_wit(audio, config["WIT_KEY"])
                print("User said:", data)
                i = i + 1
                if i % 5 == 0:
                    print(i, "Sending init prompt")
                    init_prompt()
                if lock == 0:
                    lock = 1
                    response = chat.send_message(data)
                    text_response = response.candidates[0].content.parts[0].text
                    text_response = text_response.replace("*", "")
                    print(text_response)
                    subprocess.run(["flite", "-voice", "cmu_us_slt.flitevox", "-t", text_response])
                    lock = 0
                else:
                    print("locked for voice")
                
            except sr.UnknownValueError:
                subprocess.run(["flite", "-voice", "cmu_us_slt.flitevox", "-t", "Could not understand"])
            except sr.RequestError as e:
                subprocess.run(["flite", "-voice", "cmu_us_slt.flitevox", "-t", "Could not connect"])
        else:
            time.sleep(2)
            continue


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
    global i
    global lock
    data = request.get_json()
    pin = data['pin']
    if pin == config["PASSKEY"]:
        if lock == 0:
            lock = 1
            response = chat.send_message(data["message"])
            print("Response aquired")
            length = len(response.candidates)
            print(length)
            i = i + 1
            if i % 5 == 0:
                init_prompt()
            print(i)
            r = response.candidates[0].content.parts[0].text.replace("*", "")
            r.replace("\n", "\n .")
            print(r)
            r = add_spaces_between_uppercase(r)
            subprocess.run(["flite", "-voice", "cmu_us_slt.flitevox", "-t", r])
            lock = 0
            return jsonify({"message": 'done'})
        else:
            print("locked for chat")
            return jsonify({"message": "locked"})
    return jsonify({"message": "done"})

@app.route("/mic", methods=["POST"])
def control_mic():
    global mic_state
    data = request.get_json()
    pin = data['pin']
    state = data['state']
    if pin == config["PASSKEY"]:
        if state == "ON":
            mic_state = 1
            print("mic on")
            return jsonify({"message": "done"})
        elif state == "OFF":
            mic_state = 0
            print("mic off")
            return jsonify({"message": "done"})
    else:
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
    listen_to_mic()

    # Wait for the shutdown signal
    shutdown_event.wait()
