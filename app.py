import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

app = Flask(__name__)

# --- KONFIGURACIJA ---
# Tvoj Gemini API ključ
GENAI_API_KEY = "gen-lang-client-0823125900" 
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Tvoj Facebook/Instagram Access Token (onaj dugački EAARO...)
PAGE_ACCESS_TOKEN = "EAAROQVNH2UYBQgEFWFDySL..." 

# Token koji si upisao u Meta Webhook podešavanja
VERIFY_TOKEN = "samir_ai_2026"

def send_message(recipient_id, text):
    """Šalje odgovor direktno na Instagram klijentu"""
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Greška pri slanju poruke: {e}")
        return None

@app.route('/webhook', methods=['GET'])
def verify():
    """Verifikacija Webhook-a od strane Facebooka"""
    mode = request.args.get("hub.mode")
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token_sent == VERIFY_TOKEN:
        return challenge, 200
    return "Pogrešan token", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """Glavna funkcija za primanje i obradu poruka"""
    data = request.json
    
    if not data or 'entry' not in data:
        return "OK", 200

    try:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                # Proveravamo da li je u pitanju tekstualna poruka
                if 'message' in messaging_event and 'text' in messaging_event['message']:
                    sender_id = messaging_event['sender']['id']
                    user_text = messaging_event['message']['text']

                    # POJAČAN PROMPT: Ovde definišemo Samirovu ličnost
                    prompt = (
                        f"Ti si Samir, direktor prodaje u hemijskoj industriji Novix Clean. "
                        f"Tvoj ton je profesionalan, ali ljubazan. Odgovori klijentu na srpskom jeziku. "
                        f"Klijent kaže: {user_text}"
                    )
                    
                    response = model.generate_content(prompt)
                    ai_answer = response.text

                    # Slanje odgovora nazad klijentu
                    send_message(sender_id, ai_answer)
                    print(f"Samir je odgovorio korisniku {sender_id}")

    except Exception as e:
        print(f"Greška u obradi: {e}")
    
    return "OK", 200

@app.route('/')
def index():
    return "Samir AI je online i spreman!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
