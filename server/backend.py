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
import base64

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
    split_audios = []
    for idx, dialogue in enumerate(gemini_resp):
        speaker, text = list(dialogue.items())[0]
        voice = 'Fritz-PlayAI' if speaker == "Person1" else 'Arista-PlayAI'
        groq_resp = groq_client.audio.speech.create(model="playai-tts", voice=voice, input=text, response_format="mp3")
        audio_bytes = groq_resp.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        split_audios.append({"speaker": speaker, "text": text, "audio_base64": audio_base64})
    return split_audios

def get_text_to_speech_thread(gemini_resp, result_container):
    try:
        result = get_text_to_speech(gemini_resp)
        result_container.append(result)
    except Exception as e:
        print("Error in get_text_to_speech_thread:", e)
        result_container.append([])  # to avoid crash

@app.route('/getConversation', methods=['GET', 'POST'])
def getConversation():
    fetched_prompt = request.json.get('prompt', '')
    fetched_mode = request.json.get('mode', '')

    # ai : get conversation
    more_prompt = 'Make it a casual conversation.'  # default : podcast
    if fetched_mode == 'fiveyo':
        more_prompt = 'Explain the concept to a 5 year old.'
    if fetched_mode == 'funny':
        more_prompt = 'Make it funny. The conversation should be funny.'
    if fetched_mode == 'strict':
        more_prompt = 'Make it strict. The conversation should be strict.'
    additional_prompt = f'Give me a conversation between two people explaining the concept, like a podcast. Skip the extra dialogues. Stick to explaining the concept. Keep it short. Give the response in this format: [{{"Person1": "text"}}, {{"Person2": "text"}}, {{"Person1": "text"}}, ...]. {more_prompt} Dont format any text. No bold, nothing. Dont use forward or backward slashes anywhere. Dont use quotes anywhere. No punctuation except comma, fullstop, exclaimatory mark and question mark. Give me plain text only. The request is: '
    if fetched_mode == 'pdf':
        threading.Thread(target=save_pdf_to_text).start()
        additional_prompt = 'Summarize the pdf in a conversation between two people explaining the concept, like a podcast. Skip the extra dialogues. Stick to explaining the concept. Keep it short. Give the response in this format: [{"Person1": "text"}, {"Person2": "text"}, {"Person1": "text"}, ...]. Dont format any text. No bold, nothing. Dont use forward or backward slashes anywhere. Dont use quotes anywhere. No punctuation except comma, fullstop, exclaimatory mark and question mark. Give me plain text only.'
    gemini_resp = gemini_client.models.generate_content(
        model = "gemini-2.0-flash",
        contents = additional_prompt + fetched_prompt
    )
    gemini_resp = (gemini_resp.text).replace('\n', '')
    gemini_resp = json.loads(gemini_resp)

    # text -> audio
    # threading.Thread(target=get_text_to_speech, args=(gemini_resp,)).start()
    result_container = []
    thread = threading.Thread(target=get_text_to_speech_thread, args=(gemini_resp, result_container))
    thread.start()
    thread.join()  # IMPORTANT: wait for the thread to finish
    split_audios = result_container[0]
    
    # audio -> text : for conversation mode only

    if not split_audios:
        return jsonify({'error': 'Failed to generate audio'}), 500


    # research_paper = open("../public/assets/pdf_to_text.txt").read()
    return jsonify({'conversation': gemini_resp, 'speech': split_audios})



if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)