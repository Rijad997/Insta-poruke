import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

app = Flask(__name__)

# Podešavanje Geminija
GENAI_API_KEY = "gen-lang-client-0823125900"
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Tvoja tajna reč za Facebook (izmisli bilo šta, npr. 'samir_ai_2026')
VERIFY_TOKEN = "samir_ai_2026"

@app.route('/', methods=['GET'])
def verify():
    # Facebook provera pri povezivanju
    token_sent = request.args.get("hub.verify_token")
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Pogresan token", 403

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    try:
        # Uzimanje poruke sa Instagrama
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    user_text = messaging_event['message'].get('text')

                    if user_text:
                        # Slanje teksta Geminiju
                        response = model.generate_content(f"Ti si Samir, direktor prodaje hemijske industrije. Odgovori ljubazno i kratko na: {user_text}")
                        ai_answer = response.text

                        # Slanje odgovora nazad na Instagram (ovde ce nam trebati Access Token kasnije)
                        print(f"Klijent kaze: {user_text}")
                        print(f"AI kaze: {ai_answer}")
                        
    except Exception as e:
        print(f"Greska: {e}")
    
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
