# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-24 21:43
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [("campaign", "0010_auto_20160625_0134")]

    operations = [
        migrations.CreateModel(
            name="Album",
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
                ("name", models.CharField(max_length=60)),
                (
                    "slug",
                    models.SlugField(
                        help_text="A short label for an album (used in URLs)",
                        max_length=40,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="campaign.Project",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Artwork",
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
                ("img", models.ImageField(upload_to="artist/album")),
                (
                    "album",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="music.Album"
                    ),
                ),
            ],
            options={"verbose_name_plural": "Artwork"},
        ),
        migrations.CreateModel(
            name="MarketplaceURL",
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
                    "medium",
                    models.CharField(
                        choices=[
                            ("itunes", "iTunes"),
                            ("spotify", "Spotify"),
                            ("google", "Google Play Music"),
                            ("apple", "Apple Music"),
                        ],
                        help_text="The type of marketplace",
                        max_length=10,
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        help_text="The URL to the album's page", unique=True
                    ),
                ),
                (
                    "album",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="music.Album"
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="marketplaceurl", unique_together=set([("album", "medium")])
        ),
    ]
