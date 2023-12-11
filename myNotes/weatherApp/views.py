from django.http import HttpResponseRedirect
from django.shortcuts import render
from utils.utils import get_weather


def weather(request):
    try:
        data = get_weather('Kyiv')
        print(data)
    except (KeyError, Exception) as err:
        return render(
            request,
            "weatherApp/templates/weather/weather.html",
            {
                "data": {},
                "error_message": err,
            },
        )
    else:
        # return HttpResponseRedirect(reverse("weather"))
        return render(
            request,
            "weatherApp/templates/weather/weather.html",
            {'weather': data}
        )
