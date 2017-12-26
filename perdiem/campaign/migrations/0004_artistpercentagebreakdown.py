# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-30 00:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0007_artistadmin'),
        ('campaign', '0003_auto_20160418_0057'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistPercentageBreakdown',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('displays_publicly_as', models.CharField(help_text="The name shown on the artist's detail page", max_length=30)),
                ('percentage', models.FloatField(help_text='The percentage of revenue that goes back to this group/individual (a value from 0-100)')),
                ('artist_admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='artist.ArtistAdmin')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campaign.Campaign')),
            ],
        ),
    ]
