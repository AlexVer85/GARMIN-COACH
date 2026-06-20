from flask import Flask, jsonify
from flask_cors import CORS
from garminconnect import Garmin
from datetime import date
import os

app = Flask(__name__)
CORS(app)

EMAIL = os.environ.get("GARMIN_EMAIL")
PASSWORD = os.environ.get("GARMIN_PASSWORD")

@app.route("/data")
def get_data():
    try:
        api = Garmin(EMAIL, PASSWORD)
        api.login()
        today = date.today().isoformat()
        hrv = api.get_hrv_data(today)
        sleep = api.get_sleep_data(today)
        battery = api.get_body_battery(today)
        activities = api.get_activities(0, 5)
        return jsonify({
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

@app.route("/")
def index():
    return "Garmin Coach API en ligne"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
