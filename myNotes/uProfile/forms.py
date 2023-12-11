from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Profile


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('birth_date', 'location')
