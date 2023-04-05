import os
from google.cloud import texttospeech, speech_v1p1beta1 as speech
import speech_recognition as sr
from deepl import Translator
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr



# Your DeepL API key
DEEPL_API_KEY = #Insert DeepL API Key here

# Function to get voice input and return it as text
def get_voice_input():
    client = speech.SpeechClient()

    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 3.0  # Increase the pause threshold (in seconds) as needed

    with sr.Microphone() as source:
        print("Please say something...")
        
        # Increase the timeout and phrase_time_limit values as needed
        timeout = 5  # Wait up to 5 seconds for the user to start speaking
        phrase_time_limit = 30  # Allow up to 15 seconds for a single phrase
        
        try:
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            audio_content = audio_data.get_wav_data()
        except sr.WaitTimeoutError:
            print("Timeout reached. No speech detected.")
            return None

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="en-US",
        enable_automatic_punctuation=True,
        enable_speaker_diarization=True,
        diarization_speaker_count=2,
    )

    response = client.recognize(config=config, audio=audio)

    try:
        text = response.results[0].alternatives[0].transcript
        print("You said:", text)
        return text
    except IndexError:
        print("Sorry, I didn't catch that.")
        return None
    
# Function to translate text to Spanish
def translate_to_spanish(text):
    translator = Translator(auth_key=DEEPL_API_KEY)
    translated_text = translator.translate_text(text, target_lang="ES")
    print("Translated to Spanish:", translated_text.text)  # Access the 'text' attribute
    return translated_text.text  # Return the text as a string

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = # Insert Google Cloud creditentials here. Make sure to enable the Text-to-Speech API and Speech-to-Text API

# Function to convert text to audio and play it
def text_to_audio_and_play(text, language_code="es-ES", voice_name="es-ES-Wavenet-B"):
    client = texttospeech.TextToSpeechClient()

    # Ensure that the text is a string and not empty
    if not isinstance(text, str) or not text.strip():
        print("Invalid text provided.")
        return

    input_text = texttospeech.SynthesisInput(text=text)

    voice_params = texttospeech.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    print(f"Text: {text}")
    print(f"Text Length: {len(text)}")
    print(f"Language Code: {language_code}")
    print(f"Voice Name: {voice_name}")

    try:
        response = client.synthesize_speech(
            input=input_text, voice=voice_params, audio_config=audio_config
        )
    except Exception as e:
        print("Error:", e)
        return

    with open("output.mp3", "wb") as f:
        f.write(response.audio_content)

    audio = AudioSegment.from_mp3("output.mp3")
    play(audio)
    
def list_voices(language_code="es-ES"):
    client = texttospeech.TextToSpeechClient()
    voices = client.list_voices(language_code=language_code)

    print(f"Voices for language code {language_code}:")
    for voice in voices.voices:
        print(f" - {voice.name}")

def main():
    input_text = get_voice_input()
    if input_text:
        spanish_text = translate_to_spanish(input_text)
        text_to_audio_and_play(spanish_text, voice_name="es-ES-Wavenet-B")
    #list_voices() checking available voices

if __name__ == "__main__":
    main()


