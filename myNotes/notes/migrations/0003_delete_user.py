# Generated by Django 4.2.7 on 2023-12-08 22:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("notes", "0002_user"),
    ]

    operations = [
        migrations.DeleteModel(
            name="User",
        ),
    ]