from flask import Flask, request, jsonify, render_template
import requests
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from urllib.parse import quote as url_quote  
import base64

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

CHANNEL_CONFIG = {
    "gyan": {
        "webhook": "https://discord.com/api/webhooks/...",
        "mention": "<@797057126707101716>"
    },
    "harshini": {
        "webhook": "https://discord.com/api/webhooks/...",
        "mention": "<@222222222222222222>"
    },
    "general": {
        "webhook": "https://discord.com/api/webhooks/...",
        "mention": ""
    }
}


 # --- Step 1: Download credentials from Google Drive ---
 def download_firebase_json():
     FILE_ID = "1gITR8SPOCY6E9Z_ZIRpts8shyH7_qhfp"
     URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
     PATH = "firebase-creds.json"
 
     if not os.path.exists(PATH):
         print("Downloading Firebase credentials from Google Drive...")
         r = requests.get(URL)
         with open(PATH, "wb") as f:
             f.write(r.content)
     return PATH
 
 # --- Step 2: Load Firebase Credentials ---
 cred_path = download_firebase_json()
 cred = credentials.Certificate(cred_path)
 
 firebase_admin.initialize_app(cred, {
     'databaseURL': 'https://horizon-chats-default-rtdb.asia-southeast1.firebasedatabase.app/'
 })


@app.route("/channels", methods=["GET"])
def list_channels():
    return jsonify(list(CHANNEL_CONFIG.keys()))

@app.route("/channels/<channel_name>/messages", methods=["GET", "POST"])
def messages(channel_name):
    ref = db.reference(f"messages/{channel_name}")

    if request.method == "GET":
        data = ref.order_by_key().get()
        messages_list = list(data.values()) if data else []
        return jsonify(messages_list)

    elif request.method == "POST":
        data = request.get_json()
        if not data or "user" not in data or "message" not in data:
            return jsonify({"error": "Invalid data"}), 400

        new_message = {
            "user": data["user"],
            "message": data["message"],
            "timestamp": data.get("timestamp")
        }

        ref.push(new_message)

        config = CHANNEL_CONFIG.get(channel_name)
        if config:
            payload = {
                "username": data["user"],
                "content": f"{data['message']} {config.get('mention', '')}"
            }
            try:
                requests.post(config["webhook"], json=payload)
            except Exception as e:
                print(f"Error sending to Discord ({channel_name}):", e)

        return jsonify({"status": "Message stored & sent"}), 201

@app.route("/")
def index():
    return render_template("index.html", title="Horizon Chats")

if __name__ == "__main__":
    app.run(debug=True)
