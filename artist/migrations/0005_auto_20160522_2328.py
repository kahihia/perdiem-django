# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-22 23:28
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("artist", "0004_auto_20160522_2141")]

    operations = [
        migrations.CreateModel(
            name="UpdateImage",
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
                ("img", models.ImageField(upload_to="artist/updates")),
            ],
        ),
        migrations.CreateModel(
            name="UpdateMediaURL",
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
                    "media_type",
                    models.CharField(
                        choices=[("image", "Image"), ("youtube", "YouTube")],
                        max_length=8,
                    ),
                ),
                ("url", models.URLField()),
            ],
        ),
        migrations.AddField(
            model_name="update",
            name="title",
            field=models.CharField(default="Update", max_length=75),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="update",
            name="text",
            field=models.TextField(help_text="The content of the update"),
        ),
        migrations.AddField(
            model_name="updatemediaurl",
            name="update",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="artist.Update"
            ),
        ),
        migrations.AddField(
            model_name="updateimage",
            name="update",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="artist.Update"
            ),
        ),
    ]
