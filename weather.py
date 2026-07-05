import os
import requests
import smtplib
import ssl
from email.mime.text import MIMEText

CITY = os.getenv("CITY", "Gdańsk")
API_KEY = os.getenv("WEATHER_API_KEY")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
RECIPIENTS = os.getenv("RECIPIENTS")


def get_forecast():
    url = "https://api.openweathermap.org/data/2.5/forecast"

    r = requests.get(url, params={
        "q": CITY,
        "appid": API_KEY,
        "units": "metric",
        "lang": "pl"
    })

    data = r.json()

    if "list" not in data:
        raise Exception(data)

    return data["list"]


def build_report(forecast):
    temps = []
    weather_count = {}

    for item in forecast[:8]:
        temps.append(item["main"]["temp"])
        w = item["weather"][0]["main"].lower()
        weather_count[w] = weather_count.get(w, 0) + 1

    tmin = min(temps)
    tmax = max(temps)

    main_weather = max(weather_count, key=weather_count.get)

    if "rain" in weather_count:
        icon = "🌧 Deszcz"
    elif "thunderstorm" in weather_count:
        icon = "⛈ Burza"
    elif "clouds" in weather_count:
        icon = "☁️ Zachmurzenie"
    else:
        icon = "☀️ Słonecznie"

    return f"""
🌤 Pogoda na dziś - {CITY}

🌡 Min: {tmin:.1f}°C
🌡 Max: {tmax:.1f}°C

📌 Warunki: {icon}
📊 Opis: {main_weather}
"""


def send_email(body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"Pogoda - {CITY}"
    msg["From"] = SMTP_USER
    msg["To"] = RECIPIENTS

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, RECIPIENTS, msg.as_string())


def main():
    forecast = get_forecast()
    report = build_report(forecast)
    send_email(report)
    print("OK")


if __name__ == "__main__":
    main()
