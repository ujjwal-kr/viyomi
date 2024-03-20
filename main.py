import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
from dotenv import dotenv_values
from flask import Flask, jsonify
import threading

config = dotenv_values(".env")

recogniser = sr.Recognizer()
microphone = sr.Microphone()
speaker = pyttsx3.init()
voices = speaker.getProperty('voices')
speaker.setProperty('voice', voices[1].id)
speaker.say("Hello world, I am Vyomee")
speaker.runAndWait()

r = sr.Recognizer()
mic  = sr.Microphone()
genai.configure(api_key=config["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

status = ""
app = Flask(__name__)

@app.route("/status")
def get_status():
    return jsonify({"status": status})

def start_flask_server():
    app.run()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask_server)
    flask_thread.start()

    with open("prompt.txt") as f:
        prompt = f.read()

    chat.send_message(prompt)

while True:
    print("Listening...")
    status = "listening"
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    status = "processing"
    print("Processing now")
    try:
        data = r.recognize_wit(audio, config["WIT_KEY"])
        print("User said:", data)
        response = chat.send_message(data)
        text_response = response.candidates[0].content.parts[0].text
        print(text_response)
        status = "speaking"
        speaker.say(text_response)
        speaker.runAndWait()
        
    except sr.UnknownValueError:
        speaker.say("Sorry, could not understand. Please repeat.")
        speaker.runAndWait()
    except sr.RequestError as e:
        speaker.say("Critical error occurred")
        speaker.runAndWait()
