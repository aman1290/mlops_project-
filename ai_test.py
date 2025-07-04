from microsoft_tts import edge_tts_pipeline
import simpleaudio as sa
import speech_recognition as sr
from deep_translator import GoogleTranslator
import json

# Local Tiny Llama API endpoint
app_url = "http://localhost:11434/api/generate"  # Update with your local API URL
system_role = """You are a helpful Assistant, friendly and fun, providing users with short and concise answers to their requests."""

Language = "English"  # Default language for TTS and translation

# Load language codes for translation
with open('language_code.json') as f:
    languages = json.load(f)

def llama_api(system_role, user_msg):
    """
    Call the locally running Tiny Llama API to get a response.
    """
    import requests
    try:
        payload = {
            "system_role": system_role,
            "user_msg": user_msg
        }
        response = requests.post(app_url, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "I couldn't understand that.")
        else:
            return "Error: Unable to process the request."
    except Exception as e:
        return f"Error: {str(e)}"

def tts(text, Language='English', tts_save_path=''):
    """
    Use edge TTS for generating audio from text.
    """
    Gender = "Female"
    translate_text_flag = True
    no_silence = False
    speed = 1
    long_sentence = False                          
    edge_save_path = edge_tts_pipeline(
        text,
        Language,
        Gender,
        translate_text_flag=translate_text_flag,
        no_silence=no_silence,
        speed=speed,
        tts_save_path=tts_save_path,
        long_sentence=long_sentence
    )
    print(f"Audio File Saved at: {edge_save_path}")
    return edge_save_path

def notification_sound():
    """
    Play a notification sound.
    """
    filename = "./okay.wav"
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def play_audio(text, Language='English'):
    """
    Generate and play TTS audio.
    """
    filename = 'temp.wav'
    print(f"Language: {Language}")
    tts(text, Language=Language, tts_save_path=filename)
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def chatbot(user_msg, Language='English'):
    """
    Process user message through the chatbot and play the response.
    """
    global system_role
    llama_response = llama_api(system_role, user_msg)
    print(f"Bot Response: {llama_response}")
    play_audio(llama_response, Language)

def translate_text(text, Language):
    """
    Translate the given text to the target language.
    """
    global languages
    target_language = languages[Language]
    if Language == "Chinese":
        target_language = 'zh-CN'
    translator = GoogleTranslator(target=target_language)
    translation = translator.translate(text.strip())
    return str(translation)

# Speech Recognition Config
recognizer = sr.Recognizer()
recognizer.energy_threshold = 2000
recognizer.pause_threshold = 1
recognizer.phrase_threshold = 0.1
recognizer.dynamic_energy_threshold = True
calibration_duration = 1
timeout = 10
phrase_time_limit = None

# Main Loop for Speech Recognition
while True:    
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)
            print("Listening...")
            notification_sound()
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            MyText = recognizer.recognize_google(audio_data, language=languages[Language])
            MyText = MyText.lower()
            print(f"Recognized text: {MyText}")
            
            # Translate if language is not English
            if Language != "English":
                usr_msg = translate_text(MyText, "English")
            else:
                usr_msg = MyText

            print(f"Send text: {usr_msg}")
            chatbot(usr_msg, Language)

    except Exception as e:
        print(f"Error: {str(e)}")
        continue
