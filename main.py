import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
from dotenv import dotenv_values

config = dotenv_values(".env")
print(config)

recogniser = sr.Recognizer()
microphone = sr.Microphone()
speaker = pyttsx3.init()
voices = speaker.getProperty('voices')
speaker.setProperty('voice', voices[1].id)
speaker.say("Hello world, I am Vyomee")
speaker.runAndWait()

config = dotenv_values(".env")

print(config)

r = sr.Recognizer()
mic  = sr.Microphone()
genai.configure(api_key=config["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

with open("prompt.txt") as f:
    prompt = f.read()

chat.send_message(prompt)

while True:
    print("Listening...")
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    print("Processing now...")
    try:
        data = r.recognize_wit(audio, config["WIT_KEY"])
        print("User said:", data)
        response = chat.send_message(data)
        text_response = response.candidates[0].content.parts[0].text
        print(text_response)
        speaker.say(text_response)
        speaker.runAndWait()
        
    except sr.UnknownValueError:
        speaker.say("Sorry, could not understand. Please repeat.")
        speaker.runAndWait()
    except sr.RequestError as e:
        speaker.say("Critical error occured")
        speaker.runAndWait()