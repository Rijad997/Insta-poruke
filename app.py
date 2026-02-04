import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- KONFIGURACIJA (Proveri ove podatke još jednom!) ---
PAGE_ACCESS_TOKEN = "EAAROQVNH2UYBQnTu2ZBKiG9FBp4g6c7LMpc3QaoJZApCQGFH8sueSuRJwK2bdTZB0KEZA1dvNsitn7Lbs6nXeX5YZB6v8ZAhYdkGWFDPH48cUZCTv5UXdFAwzdX2V4ZAlZAtdcGtZCZBRSZC7sJZAfEqMgacf9esc7bmqJENf8m7ZBrSAjrpowsBDcMsolfLCz2ktOZAnrWJUKb4dgUkdtIK2iZBhRgjz0qTPE8eqB4jbKLn7tTh6AZDZD"
VERIFY_TOKEN = "samir_ai_2026"
GEMINI_API_KEY = "AIzaSyDzVTe6Or8WAAnJeJiMOY_gwoEXkNkf6hc"

# Podešavanje AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def send_message(recipient_id, text):
    """Šalje odgovor i detaljno ispisuje rezultat u logove"""
    url = f"https://graph.facebook.com/v24.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    
    try:
        response = requests.post(url, json=payload)
        status = response.status_code
        res_data = response.json()
        
        if status == 200:
            print(f"✅ USPEH: Poruka poslata korisniku {recipient_id}")
        elif status == 401:
            print(f"❌ GREŠKA 401: Token je istekao ili je nevažeći! Generiši novi na Meta panelu.")
        elif status == 403:
            print(f"❌ GREŠKA 403: Nedostaju dozvole! Proveri 'Allow Access to Messages' na telefonu.")
        else:
            print(f"⚠️ STATUS {status}: {res_data}")
        return res_data
    except Exception as e:
        print(f"🚨 KRITIČNA GREŠKA pri slanju: {e}")
        return None

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Pogrešan Verify Token", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"📩 Nova aktivnost na nalogu!") # Javlja nam da je poruka uopšte stigla
    
    if data and 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                if 'message' in messaging_event and 'text' in messaging_event['message']:
                    sender_id = messaging_event['sender']['id']
                    user_text = messaging_event['message']['text']
                    
                    print(f"💬 Korisnik kaže: {user_text}")
                    
                    try:
                        # AI Razmišljanje
                        prompt = f"Ti si Samir, direktor prodaje Novix Clean. Odgovori ljubazno: {user_text}"
                        ai_response = model.generate_content(prompt)
                        ai_answer = ai_response.text
                        
                        # Slanje
                        send_message(sender_id, ai_answer)
                    except Exception as ai_err:
                        print(f"🚨 Greška u AI modulu: {ai_err}")
                        send_message(sender_id, "Izvinite, trenutno imam tehničkih poteškoća.")

    return "OK", 200

@app.route('/')
def index():
    return "Samir AI Detektiv je online!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
