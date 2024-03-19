import pyttsx3
import speech_recognition as sr
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

while True:
    print("Listening...")
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    print("Processing now...")
    try:
        data = r.recognize_wit(audio, config["WIT_KEY"])
        print("User said:", data)
        # Add your processing logic here
        
    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
    except sr.RequestError as e:
        print("Error processing the request; {0}".format(e))
