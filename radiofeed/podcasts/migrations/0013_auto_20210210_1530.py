# Generated by Django 3.1.6 on 2021-02-10 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0012_podcast_search_trigger_with_extracted_text"),
    ]

    operations = [
        migrations.AlterField(
            model_name="podcast",
            name="id",
            field=models.BigAutoField(
                editable=False, primary_key=True, serialize=False
            ),
        ),
    ]