"""Define classes for creation app forms"""
from django.forms import ModelForm, Textarea, TextInput

from .models import Note


class CreateNoteForm(ModelForm):
    """Create form for creating new note"""
    class Meta:
        model = Note
        fields = ["title", "desc", "deadline", "weight", "type"]
        widgets = {
            'desc': Textarea(attrs={'rows': 5}),
            'deadline': TextInput(attrs={'type': "date"}),
        }


class UpdateNoteForm(ModelForm):
    """Create form for updating note"""
    class Meta:
        model = Note
        fields = ["title", "desc", "deadline", "weight", "type", "isComplete"]
        widgets = {
            'desc': Textarea(attrs={'rows': 5}),
            'deadline': TextInput(attrs={'type': "date"}),
        }
