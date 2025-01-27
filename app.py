from flask import Flask, request, jsonify, render_template
import os
import json

app = Flask(__name__)

# Directory to store channel message files
MESSAGE_DIR = "messages"
os.makedirs(MESSAGE_DIR, exist_ok=True)

def get_channel_file(channel_name):
    return os.path.join(MESSAGE_DIR, f"{channel_name}.json")

def load_messages(channel_name):
    file_path = get_channel_file(channel_name)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_messages(channel_name, messages):
    file_path = get_channel_file(channel_name)
    with open(file_path, "w") as f:
        json.dump(messages, f, indent=4)

@app.route("/channels", methods=["GET"])
def list_channels():
    # List all channel JSON files in the MESSAGE_DIR
    channels = [
        os.path.splitext(filename)[0]
        for filename in os.listdir(MESSAGE_DIR)
        if filename.endswith(".json")
    ]
    return jsonify(channels)

@app.route("/channels/<channel_name>/messages", methods=["GET", "POST"])
def messages(channel_name):
    if request.method == "GET":
        # Get all messages for a channel
        messages = load_messages(channel_name)
        return jsonify(messages)

    elif request.method == "POST":
        # Add a new message to a channel
        data = request.get_json()
        if not data or "user" not in data or "message" not in data:
            return jsonify({"error": "Invalid data"}), 400

        messages = load_messages(channel_name)
        new_message = {
            "user": data["user"],
            "message": data["message"],
            "timestamp": data.get("timestamp")  # Optional timestamp
        }
        messages.append(new_message)
        save_messages(channel_name, messages)

        return jsonify(new_message), 201

@app.route("/")
def index():
    return render_template("index.html", title="Horizon Chats - Genral Channel")

if __name__ == "__main__":
    app.run(debug=True)
