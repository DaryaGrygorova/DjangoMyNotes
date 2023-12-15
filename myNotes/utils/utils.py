"""Utils"""
import json
from datetime import date, datetime, timedelta

import requests
from django.conf import settings

BASE_URL = settings.WEATHER_BASE_URL
API_KEY = settings.WEATHER_API_KEY


def get_weather(city="Kyiv"):
    """Gets and returns weather info"""
    url = f"{BASE_URL}?q={city}&units=metric&appid={API_KEY}"
    try:
        response = requests.get(url, timeout=(10, 10))

        data = json.loads(response.text)

        if data["cod"] in [200, "200"]:
            weather_info = {
                "location": f'{data["name"]}, {data["sys"]["country"]}',
                "temp": round(data["main"]["temp"]),
                "icon": data["weather"][0]["icon"],
                "feels_like": round(data["main"]["feels_like"]),
                "description": data["weather"][0]["description"],
                "wind": {
                    "speed": data["wind"]["speed"],
                    "gust": data["wind"].get("gust", "-"),
                },
            }

            return weather_info

        if data["cod"] in [404, "404"]:
            print(f'City with name "{city}" not found!')
            get_weather(city="Kyiv")
            return None

        raise ConnectionError(
            f'Something went wrong! Response with code {data["cod"]}: {data.get("message", "")}'
        )

    except ConnectionError as err:
        print(f"Something went wrong! {err}")

    return None


def get_last_monday(today_date=date.today()):
    """Define the date of last Monday"""
    current_week_day = datetime.isoweekday(today_date)
    delta_days = 1 - current_week_day

    if delta_days == 0:
        return today_date

    monday_date = today_date + timedelta(days=delta_days)
    return monday_date
