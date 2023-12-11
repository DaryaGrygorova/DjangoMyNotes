from django.urls import path, include

from .views import update_profile

urlpatterns = [
    path("", update_profile, name='update-profile'),
]
