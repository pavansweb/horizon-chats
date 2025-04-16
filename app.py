from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# In-memory message storage
channel_messages = {}

# Unified channel config
CHANNEL_CONFIG = {
    "gyan": {
        "webhook": "https://discord.com/api/webhooks/1361999839172362423/KxV_ROvNfdAfE-0gvuNSA7SjRJ09w6eNm3D6JQ_Wz9xZ4ql2GBChekIMc92KKUOMHIyZ",
        "mention": "<@111111111111111111>"
    },
    "harshini": {
        "webhook": "https://discord.com/api/webhooks/1362014671246459012/4UI-3CvLW3XGNKbgi4IBwjxdeGdkWlPzciCy0Fl6hyv0jLStt3Gx6LbBI71PoUlW7mLe",
        "mention": "<@222222222222222222>"
    },
    "general": {
        "webhook": "https://discord.com/api/webhooks/1362084467233132796/0zjYT6RXh99GFlD24wqc7Bnd-n8rro6RJ-PXvhd5pDD5Y5-ummDuR5eOlPv4rdP3M1SS",
        "mention": " "
    },
    # Add more channels as needed
}

@app.route("/channels", methods=["GET"])
def list_channels():
    return jsonify(list(CHANNEL_CONFIG.keys()))


@app.route("/channels/<channel_name>/messages", methods=["GET", "POST"])
def messages(channel_name):
    if request.method == "GET":
        return jsonify(channel_messages.get(channel_name, []))

    elif request.method == "POST":
        data = request.get_json()
        if not data or "user" not in data or "message" not in data:
            return jsonify({"error": "Invalid data"}), 400

        new_message = {
            "user": data["user"],
            "message": data["message"],
            "timestamp": data.get("timestamp")
        }

        # Save in memory
        channel_messages.setdefault(channel_name, []).append(new_message)

        # Send to Discord if channel config exists
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

        return jsonify(new_message), 201

@app.route("/")
def index():
    return render_template("index.html", title="How to understand concepts faster")

if __name__ == "__main__":
    app.run(debug=True)
