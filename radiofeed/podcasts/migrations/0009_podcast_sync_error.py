# Generated by Django 3.1.5 on 2021-01-23 09:48

# Django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0008_podcast_recipients"),
    ]

    operations = [
        migrations.AddField(
            model_name="podcast",
            name="sync_error",
            field=models.TextField(blank=True),
        ),
    ]
