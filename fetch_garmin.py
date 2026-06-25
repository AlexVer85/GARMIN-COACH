import os
import json
from datetime import date, datetime
from garminconnect import Garmin

email = os.environ["GARMIN_EMAIL"]
password = os.environ["GARMIN_PASSWORD"]

api = Garmin(email, password)
api.login()

today = date.today().isoformat()

hrv = api.get_hrv_data(today)
sleep = api.get_sleep_data(today)
battery = api.get_body_battery(today)
activities = api.get_activities(0, 5)

data = {
    "date": today,
    "fetched_at": datetime.utcnow().isoformat(),
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
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Done: {today} at {data['fetched_at']}")
