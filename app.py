import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

app = Flask(__name__)

# Podešavanje Geminija
# NAPOMENA: Ovaj API ključ treba da bude tvoj stvarni ključ iz Google AI Studio
GENAI_API_KEY = "gen-lang-client-0823125900" 
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Tvoja tajna reč za Facebook verifikaciju
VERIFY_TOKEN = "samir_ai_2026"

@app.route('/webhook', methods=['GET'])
def verify():
    # Facebook provera pri povezivanju (Webhook Verification)
    mode = request.args.get("hub.mode")
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token_sent == VERIFY_TOKEN:
        print("Webhook verifikovan uspešno!")
        return challenge, 200
    
    print("Verifikacija neuspešna: Pogrešan token ili mod.")
    return "Pogresan token", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    # Primanje poruka sa Instagrama
    data = request.json
    try:
        if data.get('entry'):
            for entry in data['entry']:
                for messaging_event in entry.get('messaging', []):
                    if messaging_event.get('message'):
                        sender_id = messaging_event['sender']['id']
                        user_text = messaging_event['message'].get('text')

                        if user_text:
                            # Slanje teksta Geminiju
                            prompt = f"Ti si Samir, direktor prodaje hemijske industrije. Odgovori ljubazno i kratko na: {user_text}"
                            response = model.generate_content(prompt)
                            ai_answer = response.text

                            print(f"Klijent ({sender_id}) kaže: {user_text}")
                            print(f"AI (Samir) kaže: {ai_answer}")
                            
                            # OVDE ĆE NAM KASNIJE TREBATI FACEBOOK ACCESS TOKEN ZA SLANJE ODGOVORA
                            
    except Exception as e:
        print(f"Greska u obradi poruke: {e}")
    
    return "OK", 200

@app.route('/')
def index():
    return "Server je aktivan i radi!", 200

if __name__ == "__main__":
    # Render koristi port 10000 ili onaj koji on dodeli
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
