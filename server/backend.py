# import pymupdf
import pdfplumber
from google import genai
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from groq import Groq
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import json
import threading
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4200", "http://127.0.0.1:4200"], "methods": ["GET", "POST", "OPTIONS"]}}, allow_headers=["Access-Control-Allow-Methods", "Access-Control-Allow-Origin", "Content-Type", "Access-Control-Allow-Headers"], supports_credentials=True)

load_dotenv()
GEMINI_APIKEY = os.environ['GEMINI_APIKEY']
gemini_client = genai.Client(api_key=GEMINI_APIKEY)
GROQ_APIKEY = os.environ['GROQ_APIKEY']
groq_client = Groq(api_key=GROQ_APIKEY)
ELEVENLABS_APIKEY = os.environ['ELEVENLABS_APIKEY']
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_APIKEY)

def save_pdf_to_text():
    out = open('assets/pdf_to_text.txt', 'ab')
    with pdfplumber.open('assets/research-paper.pdf') as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            out.write(text.encode('utf-8'))
    out.close()

def get_text_to_speech(gemini_resp):
    try:
        with open("assets/text_to_speech.mp3", "wb") as f:
            for entry in gemini_resp:
                for speaker, text in entry.items():
                    voice = "Rachel" if speaker == "Person1" else "Sam"
                audio_generator = elevenlabs_client.generate(text=text, voice=voice, model="eleven_monolingual_v1")
                for chunk in audio_generator:
                    f.write(chunk)
        speech_generated = 'True'
    except Exception as e:
        print(f"Error in get_text_to_speech thread: {e}")

@app.route('/getConversation', methods=['GET', 'POST'])
def getConversation():
    speech_generated = 'False'

    # pdf -> text
    # threading.Thread(target=save_pdf_to_text).start()

    # ai : get conversation
    fetched_prompt = request.json.get('prompt', '')
    additional_prompt = 'Give me a conversation between two people explaining the concept, like a podcast. Skip the extra dialogues. Stick to explaining the concept. Keep it short. Give the response in this format: [{"Person1": "text"}, {"Person2": "text"}, {"Person1": "text"}, ...]. Dont format any text. No bold, nothing. Dont use forward or backward slashes anywhere. Dont use quotes anywhere. No punctuation except comma, fullstop, exclaimatory mark and question mark. Give me plain text only. The request is: '
    gemini_resp = gemini_client.models.generate_content(
        model = "gemini-2.0-flash",
        contents = additional_prompt + fetched_prompt
    )
    gemini_resp = (gemini_resp.text).replace('\n', '')
    gemini_resp = json.loads(gemini_resp)

    # text -> audio : for podcast
    threading.Thread(target=get_text_to_speech, args=(gemini_resp,)).start()

    # speech_file_path = "speech.wav" 
    # model = "playai-tts"
    # voice = "Fritz-PlayAI"
    # text = gemini_resp.text
    # response_format = "wav"
    # groq_resp = groq_client.audio.speech.create(
    #     model=model,
    #     voice=voice,
    #     input=text,
    #     response_format=response_format
    # )
    # groq_resp.write_to_file(speech_file_path)

    # audio -> text : for conversation mode only

    # research_paper = open("../public/assets/pdf_to_text.txt").read()
    return jsonify({'conversation': gemini_resp, 'speech_generated': speech_generated})



if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)