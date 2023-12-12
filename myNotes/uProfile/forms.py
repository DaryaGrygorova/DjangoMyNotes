"""Define classes for creation app forms"""
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Profile


class UserForm(ModelForm):
    """Create form for User data"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(ModelForm):
    """Create form for user profile data"""
    class Meta:
        model = Profile
        fields = ('birth_date', 'location')
