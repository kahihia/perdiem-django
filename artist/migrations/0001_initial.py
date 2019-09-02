# Generated by Django 1.9.4 on 2016-03-13 08:06
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Artist",
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
                ("name", models.CharField(db_index=True, max_length=60)),
                ("slug", models.SlugField(max_length=40)),
                (
                    "lat",
                    models.DecimalField(
                        db_index=True,
                        decimal_places=4,
                        help_text="Latitude of artist location",
                        max_digits=6,
                    ),
                ),
                (
                    "lon",
                    models.DecimalField(
                        db_index=True,
                        decimal_places=4,
                        help_text="Longitude of artist location",
                        max_digits=7,
                    ),
                ),
                (
                    "location",
                    models.CharField(
                        help_text="Description of artist location (usually city, state, country format)",
                        max_length=40,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Bio",
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
                    "bio",
                    models.TextField(
                        help_text="Short biography of artist. May contain HTML."
                    ),
                ),
                (
                    "artist",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="artist.Artist"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Genre",
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
                ("name", models.CharField(db_index=True, max_length=40, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Photo",
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
                    "img",
                    models.ImageField(
                        help_text="Primary profile photo of artist", upload_to="artist"
                    ),
                ),
                (
                    "artist",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="artist.Artist"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Social",
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
                            ("facebook", "Facebook"),
                            ("twitter", "Twitter"),
                            ("instagram", "Instagram"),
                            ("youtube", "YouTube"),
                            ("soundcloud", "SoundCloud"),
                        ],
                        help_text="The type of social network",
                        max_length=10,
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        help_text="The URL to the artist's social network page",
                        unique=True,
                    ),
                ),
                (
                    "artist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="artist.Artist"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SoundCloudPlaylist",
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
                    "playlist",
                    models.URLField(
                        help_text="The SoundCloud iframe URL to the artist's playlist",
                        unique=True,
                    ),
                ),
                (
                    "artist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="artist.Artist"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Update",
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
                    "created_datetime",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                (
                    "text",
                    models.TextField(
                        help_text="The content of the update. May contain HTML."
                    ),
                ),
                (
                    "artist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="artist.Artist"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="artist",
            name="genres",
            field=models.ManyToManyField(to="artist.Genre"),
        ),
        migrations.AlterUniqueTogether(
            name="social", unique_together={("artist", "medium")}
        ),
    ]
