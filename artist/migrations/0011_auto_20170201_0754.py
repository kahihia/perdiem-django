# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-01 07:54
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("artist", "0010_auto_20170201_0754")]

    operations = [
        migrations.RemoveField(model_name="soundcloudplaylist", name="artist"),
        migrations.DeleteModel(name="SoundCloudPlaylist"),
    ]
