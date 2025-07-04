from flask import Flask, jsonify, request, render_template
import requests
import pyttsx3
import speech_recognition as sr
import logging
from queue import Queue
from time import sleep

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# TinyLlama API details
TINYLLAMA_URL = 'http://localhost:11434/api/generate'
HEADERS = {"Content-Type": "application/json"}

# Queue for managing TTS tasks
tts_queue = Queue()

# Flag for TTS loop
tts_running = False

def query_tinyllama(prompt):
    """
    Interact with TinyLlama API to get the response for a given prompt.
    """
    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
    }
    try:
        response = requests.post(TINYLLAMA_URL, json=payload, headers=HEADERS)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json().get("response", "No response from model.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error interacting with TinyLlama: {e}")
        return "Sorry, I couldn't process your request."


def recognize_speech():
    """
    Recognize speech input from the user using SpeechRecognition.
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    try:
        with microphone as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source)
            logging.info("Listening for speech...")
            audio = recognizer.listen(source)

        logging.info("Recognizing speech...")
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        logging.warning("Speech recognition could not understand the audio.")
        return "Sorry, I couldn't understand what you said."
    except sr.RequestError as e:
        logging.error(f"Error with the speech recognition service: {e}")
        return "Speech recognition service is unavailable."


def tts_loop():
    """
    Continuous loop for processing TTS tasks.
    """
    global tts_running
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)  # Speech rate
    tts_engine.setProperty('volume', 0.9)  # Volume level

    while True:
        if not tts_queue.empty():
            text = tts_queue.get()
            try:
                logging.info("Speaking the response...")
                tts_engine.say(text)
                tts_engine.runAndWait()
                logging.info("Finished speaking.")
            except Exception as e:
                logging.error(f"Error in TTS: {e}")
        else:
            sleep(0.1)  # Small delay to prevent excessive CPU usage


def enqueue_tts(text):
    """
    Add text to the TTS queue for speaking.
    """
    logging.info(f"Enqueueing text for TTS: {text}")
    tts_queue.put(text)


def shorten_response(text, max_sentences=2):
    """
    Shorten the response to the specified number of sentences.
    """
    sentences = text.split('.')
    shortened = '. '.join(sentences[:max_sentences]).strip()
    return shortened + '.' if not shortened.endswith('.') else shortened


@app.route('/')
def index():
    """
    Serve the main webpage.
    """
    return render_template('index.html')  # Ensure index.html is in the templates folder


@app.route('/api/voice', methods=['POST'])
def handle_voice_input():
    """
    Handle voice input from the frontend.
    """
    user_input = request.json.get('text', '')

    if not user_input:
        return jsonify({'error': 'No input received'}), 400

    if user_input.lower() == "stop":
        response_text = "Goodbye. I am waiting for the next question."
        enqueue_tts(response_text)
        return jsonify({'response': response_text})

    response_text = query_tinyllama(user_input)
    short_response = shorten_response(response_text)
    enqueue_tts(short_response)

    return jsonify({'response': short_response})


@app.route('/api/speech', methods=['GET'])
def handle_speech_input():
    """
    Handle speech input from the user via the backend.
    """
    user_input = recognize_speech()

    if user_input.lower() == "stop":
        response_text = "Goodbye. I am waiting for the next question."
        enqueue_tts(response_text)
        return jsonify({'response': response_text})

    response_text = query_tinyllama(user_input)
    short_response = shorten_response(response_text)
    enqueue_tts(short_response)

    return jsonify({'response': short_response})


if __name__ == '__main__':
    logging.info("Starting the Flask app...")
    
    # Start the TTS loop in a separate thread to avoid blocking Flask
    from threading import Thread
    tts_thread = Thread(target=tts_loop, daemon=True)
    tts_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
