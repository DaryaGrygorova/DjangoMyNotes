from datetime import date
from django.db import models
from django.contrib.auth import get_user_model

from utils.constants import WEIGHT_CHOICES, TYPE_CHOICES

User = get_user_model()


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    isComplete = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(default=date.today)
    weight = models.CharField(max_length=20, choices=WEIGHT_CHOICES, default='Normal')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='To do')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['isComplete']
        