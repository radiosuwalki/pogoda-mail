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
    params = {
        "q": CITY,
        "appid": API_KEY,
        "units": "metric",
        "lang": "pl"
    }

    data = requests.get(url, params=params).json()
    return data["list"]


def build_report(forecast):
    temps = []
    rain_hours = []
    weather_count = {}

    for item in forecast[:8]:  # ~24h (3h interval)
        temp = item["main"]["temp"]
        temps.append(temp)

        weather = item["weather"][0]["main"].lower()
        weather_count[weather] = weather_count.get(weather, 0) + 1

        if "rain" in item or "Rain" in item.get("weather", [{}])[0]["main"]:
            rain_hours.append(item["dt_txt"])

    t_min = min(temps)
    t_max = max(temps)

    dominant = max(weather_count, key=weather_count.get)

    if "thunderstorm" in weather_count:
        category = "⛈ Burza"
    elif "rain" in weather_count:
        category = "🌧 Deszcz"
    elif "clouds" in weather_count:
        category = "☁️ Zachmurzenie"
    elif "clear" in weather_count:
        category = "☀️ Słoneczne"
    else:
        category = "🌤 Zmienna pogoda"

    rain_text = ""
    if rain_hours:
        rain_text = "\nOpady możliwe około:\n" + "\n".join(rain_hours)

    return f"""
🌤 Pogoda na dziś - {CITY}

📊 Temperatura:
- Min: {t_min:.1f}°C
- Max: {t_max:.1f}°C

📌 Typ dnia: {category}

🌦 Opis: {dominant}
{rain_text}

Miłego dnia!
"""


def send_email(body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"Pogoda na dziś - {CITY}"
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
    print("OK - wysłano pogodę dnia")


if __name__ == "__main__":
    main()
