# Generated by Django 1.10.1 on 2016-09-10 23:12
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("music", "0003_auto_20160730_1802")]

    operations = [
        migrations.CreateModel(
            name="Track",
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
                ("disc_number", models.PositiveSmallIntegerField(default=1)),
                ("track_number", models.PositiveSmallIntegerField()),
                ("name", models.CharField(max_length=60)),
                ("duration", models.DurationField(blank=True, null=True)),
                (
                    "album",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="music.Album"
                    ),
                ),
            ],
        )
    ]
