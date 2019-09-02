# Generated by Django 1.9.6 on 2016-05-14 05:28
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0002_userprofiles"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserAvatar",
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
                    "provider",
                    models.CharField(
                        choices=[
                            ("perdiem", "PerDiem"),
                            ("google-oauth2", "Google"),
                            ("facebook", "Facebook"),
                        ],
                        max_length=15,
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
        migrations.CreateModel(
            name="UserAvatarImage",
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
                ("img", models.ImageField(upload_to=b"")),
                (
                    "avatar",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.UserAvatar",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserAvatarURL",
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
                ("url", models.URLField()),
                (
                    "avatar",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.UserAvatar",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="userprofile",
            name="avatar",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="accounts.UserAvatar",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="useravatar", unique_together={("user", "provider")}
        ),
    ]
