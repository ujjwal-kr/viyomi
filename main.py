import pyttsx3
speaker = pyttsx3.init()
voices = speaker.getProperty('voices')
speaker.setProperty('voice', voices[1].id) 
speaker.say("Hello world, I am Vyomee")
speaker.runAndWait()