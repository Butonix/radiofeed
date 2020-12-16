# Generated by Django 3.1.3 on 2020-12-16 12:59

# Django
import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

# Third Party Libraries
import model_utils.fields


class Migration(migrations.Migration):

    replaces = [
        ("episodes", "0001_initial"),
        ("episodes", "0002_auto_20201207_2206"),
        ("episodes", "0003_auto_20201213_1448"),
        ("episodes", "0004_auto_20201213_2202"),
        ("episodes", "0005_episode_search_trigger"),
        ("episodes", "0006_auto_20201214_0852"),
        ("episodes", "0007_auto_20201214_2307"),
        ("episodes", "0008_auto_20201214_2327"),
        ("episodes", "0009_auto_20201216_0854"),
        ("episodes", "0010_auto_20201216_1254"),
    ]

    initial = True

    dependencies = [
        ("podcasts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Episode",
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
                ("guid", models.TextField()),
                ("pub_date", models.DateTimeField()),
                ("link", models.URLField(blank=True, max_length=500, null=True)),
                ("title", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
                ("keywords", models.TextField(blank=True)),
                ("media_url", models.URLField(max_length=500)),
                ("media_type", models.CharField(max_length=20)),
                ("length", models.IntegerField(blank=True, null=True)),
                ("duration", models.CharField(blank=True, max_length=12)),
                ("explicit", models.BooleanField(default=False)),
                (
                    "podcast",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcasts.podcast",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(
                fields=["podcast"], name="episodes_ep_podcast_3361d9_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(fields=["guid"], name="episodes_ep_guid_b00554_idx"),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(
                fields=["-pub_date"], name="episodes_ep_pub_dat_205e36_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(
                fields=["pub_date"], name="episodes_ep_pub_dat_60d1c1_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(fields=["title"], name="episodes_ep_title_4a6059_idx"),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(fields=["-title"], name="episodes_ep_title_ce2893_idx"),
        ),
        migrations.AddConstraint(
            model_name="episode",
            constraint=models.UniqueConstraint(
                fields=("podcast", "guid"), name="unique_episode"
            ),
        ),
        migrations.CreateModel(
            name="Bookmark",
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
            model_name="bookmark",
            index=models.Index(
                fields=["-created"], name="episodes_bo_created_d69e08_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="bookmark",
            constraint=models.UniqueConstraint(
                fields=("user", "episode"), name="uniq_bookmark"
            ),
        ),
        migrations.AlterField(
            model_name="episode",
            name="duration",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.RemoveIndex(
            model_name="episode", name="episodes_ep_title_4a6059_idx",
        ),
        migrations.RemoveIndex(
            model_name="episode", name="episodes_ep_title_ce2893_idx",
        ),
        migrations.AddField(
            model_name="episode",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                editable=False, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="episodes_ep_search__466ef4_gin"
            ),
        ),
        migrations.RunSQL(
            sql="\n            CREATE TRIGGER episode_update_search_trigger\n            BEFORE INSERT OR UPDATE OF title, keywords, search_vector\n            ON episodes_episode\n            FOR EACH ROW EXECUTE PROCEDURE\n            tsvector_update_trigger(\n              search_vector, 'pg_catalog.english', title, keywords);\n            UPDATE episodes_episode SET search_vector = NULL;\n            ",
            reverse_sql="\n            DROP TRIGGER IF EXISTS episode_update_search_trigger\n            ON episodes_episode;\n            ",
        ),
        migrations.AlterField(
            model_name="episode",
            name="media_type",
            field=models.CharField(max_length=60),
        ),
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
        migrations.AlterField(
            model_name="history",
            name="completed",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RemoveIndex(
            model_name="history", name="episodes_hi_complet_ebe4aa_idx",
        ),
        migrations.RemoveField(model_name="history", name="completed",),
        migrations.RenameModel(old_name="History", new_name="AudioLog",),
        migrations.RemoveConstraint(model_name="audiolog", name="uniq_history",),
        migrations.RemoveIndex(
            model_name="audiolog", name="episodes_hi_updated_29f4e9_idx",
        ),
        migrations.AddIndex(
            model_name="audiolog",
            index=models.Index(
                fields=["-updated"], name="episodes_au_updated_eb4a9e_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="audiolog",
            constraint=models.UniqueConstraint(
                fields=("user", "episode"), name="uniq_audio_log"
            ),
        ),
    ]
