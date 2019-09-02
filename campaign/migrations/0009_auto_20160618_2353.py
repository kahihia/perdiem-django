# Generated by Django 1.9.7 on 2016-06-18 23:53
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("campaign", "0008_auto_20160618_2352")]

    operations = [
        migrations.AlterField(
            model_name="artistpercentagebreakdown",
            name="project",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="campaign.Project",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="revenuereport",
            name="project",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="campaign.Project",
            ),
            preserve_default=False,
        ),
        migrations.RemoveField(model_name="artistpercentagebreakdown", name="campaign"),
        migrations.RemoveField(model_name="revenuereport", name="campaign"),
    ]
