# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-25 02:26
from django.db import migrations, models
import django.db.models.deletion
import music.models


class Migration(migrations.Migration):

    dependencies = [("music", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Audio",
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
                ("file", music.models.S3PrivateFileField(upload_to="artist/audio")),
                (
                    "album",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="music.Album"
                    ),
                ),
            ],
            options={"verbose_name_plural": "Audio"},
        ),
        migrations.AlterField(
            model_name="marketplaceurl",
            name="medium",
            field=models.CharField(
                choices=[
                    ("spotify", "Spotify"),
                    ("itunes", "iTunes"),
                    ("apple", "Apple Music"),
                    ("google", "Google Play"),
                    ("amazon", "Amazon"),
                    ("tidal", "Tidal"),
                    ("youtube", "YouTube"),
                ],
                help_text="The type of marketplace",
                max_length=10,
            ),
        ),
    ]
