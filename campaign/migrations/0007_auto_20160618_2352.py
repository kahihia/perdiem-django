# Generated by Django 1.9.7 on 2016-06-18 23:52
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("campaign", "0006_auto_20160618_2351")]

    operations = [
        migrations.AlterField(
            model_name="campaign",
            name="project",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="campaign.Project",
            ),
            preserve_default=False,
        ),
        migrations.RemoveField(model_name="campaign", name="artist"),
        migrations.RemoveField(model_name="campaign", name="reason"),
        migrations.AddField(
            model_name="artistpercentagebreakdown",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="campaign.Project",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="revenuereport",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="campaign.Project",
            ),
            preserve_default=False,
        ),
    ]
