from flask import Flask, request, jsonify, render_template
import sqlite3, requests, os

app = Flask(__name__)
DB_FILE = "chat.db"

# Discord webhook config
CHANNEL_CONFIG = {
    "gyan": {
        "webhook": "https://discord.com/api/webhooks/...",
        "mention": "<@111111111111111111>"
    },
    "harshini": {
        "webhook": "https://discord.com/api/webhooks/...",
        "mention": "<@222222222222222222>"
    },
    "general": {
        "webhook": "https://discord.com/api/webhooks/...",
        "mention": " "
    },
}

# Fetch DB from GitHub if not exists
def download_db():
    if not os.path.exists(DB_FILE):
        url = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/chat.db"
        r = requests.get(url)
        with open(DB_FILE, "wb") as f:
            f.write(r.content)
        print("Downloaded DB from GitHub.")

download_db()

# Init DB if not exists
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel TEXT,
                user TEXT,
                message TEXT,
                timestamp TEXT
            )
        """)
init_db()

@app.route("/channels", methods=["GET"])
def list_channels():
    return jsonify(list(CHANNEL_CONFIG.keys()))

@app.route("/channels/<channel_name>/messages", methods=["GET", "POST"])
def messages(channel_name):
    if request.method == "GET":
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.execute("SELECT user, message, timestamp FROM messages WHERE channel=? ORDER BY id", (channel_name,))
            rows = cursor.fetchall()
            return jsonify([{"user": row[0], "message": row[1], "timestamp": row[2]} for row in rows])

    elif request.method == "POST":
        data = request.get_json()
        if not data or "user" not in data or "message" not in data:
            return jsonify({"error": "Invalid data"}), 400

        # Save to database
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "INSERT INTO messages (channel, user, message, timestamp) VALUES (?, ?, ?, ?)",
                (channel_name, data["user"], data["message"], data.get("timestamp"))
            )

        # Send to Discord
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
