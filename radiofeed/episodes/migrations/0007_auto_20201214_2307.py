# Generated by Django 3.1.3 on 2020-12-14 23:07

# Django
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

# Third Party Libraries
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("episodes", "0006_auto_20201214_0852"),
    ]

    operations = [
        migrations.CreateModel(
            name="History",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("updated", models.DateTimeField()),
                ("completed", models.DateTimeField()),
                ("current_time", models.IntegerField(default=0)),
                (
                    "episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="episodes.episode",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="history",
            index=models.Index(
                fields=["-updated"], name="episodes_hi_updated_29f4e9_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="history",
            index=models.Index(
                fields=["-completed"], name="episodes_hi_complet_ebe4aa_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="history",
            constraint=models.UniqueConstraint(
                fields=("user", "episode"), name="uniq_history"
            ),
        ),
    ]
