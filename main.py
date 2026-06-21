from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
from garminconnect import Garmin
from datetime import date
import os
import requests

app = Flask(__name__)
CORS(app)

@app.route("/")
@app.route("/app")
def serve_app():
    return send_file("app.html")

@app.route("/data")
def get_data():
    email = os.environ.get("GARMIN_EMAIL", "")
    password = os.environ.get("GARMIN_PASSWORD", "")
    if not email or not password:
        return jsonify({"error": "Variables manquantes"}), 500
    try:
        api = Garmin(email, password)
        api.login()
        today = date.today().isoformat()
        hrv = api.get_hrv_data(today)
        sleep = api.get_sleep_data(today)
        battery = api.get_body_battery(today)
        activities = api.get_activities(0, 5)
        return jsonify({
            "date": today,
            "hrv": hrv.get("hrvSummary", {}) if hrv else {},
            "sleep": sleep.get("dailySleepDTO", {}) if sleep else {},
            "body_battery": battery[0] if battery else {},
            "activities": [
                {
                    "name": a.get("activityName"),
                    "type": a.get("activityType", {}).get("typeKey"),
                    "date": a.get("startTimeLocal", "")[:10],
                    "duration": round(a.get("duration", 0) / 60),
                    "hrAvg": a.get("averageHR"),
                    "calories": a.get("calories")
                } for a in activities[:5]
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        body = request.get_json()
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            json=body,
            headers=headers
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
