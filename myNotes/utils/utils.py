import json
from datetime import date, timedelta, datetime

import requests
from django.conf import settings

BASE_URL = settings.WEATHER_BASE_URL
API_KEY = settings.WEATHER_API_KEY

def get_weather(city="Kyiv"):
    url = f"{BASE_URL}?q={city}&units=metric&appid={API_KEY}"
    try:
        response = requests.get(url, timeout=(5, 5))

        data = json.loads(response.text)

        if data["cod"] in [200, "200"]:
            weather_info = {
                'location': f'{data["name"]}, {data["sys"]["country"]}',
                'temp': round(data["main"]["temp"]),
                'icon': data["weather"][0]["icon"],
                'feels_like': round(data["main"]["feels_like"]),
                'description': data["weather"][0]["description"],
                'wind': {
                    'speed': data["wind"]["speed"],
                    'gust': data["wind"].get("gust", "-"),
                },
            }

            return weather_info

        if data["cod"] in [404, "404"]:
            print(f'City with name "{city}" not found!')

        print(
            f'Something went wrong! Response with code {data["cod"]}: {data.get("message", "")}'
            )

    except ConnectionError as err:
        print(f"Connection error! {err}")


def get_last_monday(today_date=date.today()):
    current_week_day = datetime.isoweekday(today_date)
    delta_days = 1 - current_week_day

    if delta_days == 0:
        return today_date

    monday_date = today_date + timedelta(days=delta_days)
    return monday_date


if __name__ == "__main__":
    print('last_monday: ', get_last_monday(date(2023, 10, 9)))
    WEEK_DAYS = ['day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7']

    notes_week = {value: None for _, value in enumerate(WEEK_DAYS)}
    print(notes_week)