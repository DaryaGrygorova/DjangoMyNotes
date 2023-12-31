# Generated by Django 4.2.7 on 2023-12-11 00:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notes", "0003_delete_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="type",
            field=models.CharField(
                choices=[
                    ("Note", "Note"),
                    ("To do", "To do"),
                    ("Event", "Event"),
                    ("Holiday", "Holiday"),
                ],
                default="To do",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="note",
            name="weight",
            field=models.CharField(
                choices=[("Low", "Low"), ("Normal", "Normal"), ("High", "High")],
                default="Normal",
                max_length=20,
            ),
        ),
    ]
