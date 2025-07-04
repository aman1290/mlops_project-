import requests
import speech_recognition as sr
import pyttsx3

# Initialize TTS engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Speed of speech
tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

# TinyLlama API Details
url = 'http://localhost:11434/api/generate'
headers = {"Content-Type": "application/json"}

# Speech-to-Text Function to Listen for Activation Phrase
def listen_for_hello_tutor():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for activation phrase 'Hello Tutor'...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        # Convert audio to text
        command = recognizer.recognize_google(audio)
        print(f"Detected: {command}")
        if "hello tutor" in command.lower():
            return True
        else:
            return False
    except sr.UnknownValueError:
        print("Speech Recognition Error: Could not understand audio.")
        return False
    except sr.RequestError as e:
        print(f"Speech Recognition Service Error: {e}")
        return False

# Speech-to-Text Function for User Queries
def listen_to_query():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your query...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        # Convert audio to text
        text = recognizer.recognize_google(audio)
        print(f"User Query Detected: {text}")
        return text
    except sr.UnknownValueError:
        print("Speech Recognition Error: Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Speech Recognition Service Error: {e}")
        return None

# Function to Query TinyLlama API
def query_tinyllama(prompt):
    data = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"API Response Status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            print(f"TinyLlama Response: {response_data}")
            return response_data.get("response", "No response received.")
        else:
            print(f"Error from TinyLlama API: {response.status_code} - {response.text}")
            return "Sorry, I couldn't process that."
    except Exception as e:
        print(f"API Interaction Error: {e}")
        return "Error interacting with the TinyLlama API."

# Text-to-Speech Function
def speak_text(text):
    print(f"TTS Output: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

# Main Logic
def main():
    print("Virtual Tutor Voice Assistant is now running...")
    while True:
        if listen_for_hello_tutor():
            speak_text("Hello Tutor, how may I help you?")
            user_query = listen_to_query()
            if user_query:
                print(f"Processing Query: {user_query}")
                ai_response = query_tinyllama(user_query)
                print(f"Assistant Response: {ai_response}")
                speak_text(ai_response)
            else:
                speak_text("I couldn't understand your question. Please try again.")

# Entry Point
if __name__ == "__main__":
    main()
