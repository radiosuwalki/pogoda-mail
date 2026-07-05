import requests
import smtplib
import ssl
from email.mime.text import MIMEText
import os

# ===== SMTP =====
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
RECIPIENTS = os.getenv("RECIPIENTS")

# ===== SUWAŁKI =====
CITY = "Suwałki"
LAT = 54.102
LON = 22.930


def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": "temperature_2m,precipitation",
        "forecast_days": 1,
        "timezone": "Europe/Warsaw"
    }

    data = requests.get(url, params=params).json()
    return data["hourly"]


def build_report(data):
    temps = data["temperature_2m"][:24]
    rain = data["precipitation"][:24]
    times = data["time"][:24]

    tmin = min(temps)
    tmax = max(temps)

    rain_hours = []

    for i, r in enumerate(rain):
        if r > 0:
            rain_hours.append(times[i][11:16])  # HH:MM

    if rain_hours:
        rain_text = "🌧 Opady możliwe około: " + ", ".join(rain_hours)
    else:
        rain_text = "☀️ Brak opadów w ciągu dnia"

    # prosta klasyfikacja dnia
    if tmax <= 0:
        day_type = "❄️ Mroźnie"
    elif tmax < 10:
        day_type = "🧥 Chłodno"
    elif tmax < 20:
        day_type = "🌤 Łagodnie"
    else:
        day_type = "☀️ Ciepło"

    return f"""
🌤 Pogoda na dziś – {CITY}

🌡 Min: {tmin:.1f}°C
🌡 Max: {tmax:.1f}°C

📌 Typ dnia: {day_type}

📍 {rain_text}

Miłego dnia!
"""


def send_email(body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"Pogoda – {CITY}"
    msg["From"] = SMTP_USER
    msg["To"] = RECIPIENTS

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, RECIPIENTS, msg.as_string())


def main():
    data = get_weather()
    report = build_report(data)
    send_email(report)
    print("OK - wysłano pogodę")


if __name__ == "__main__":
    main()
