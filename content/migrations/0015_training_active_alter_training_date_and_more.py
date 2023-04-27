# Generated by Django 4.0.6 on 2023-04-26 00:35

import content.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0014_team_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='training',
            name='date',
            field=models.DateField(default=django.utils.timezone.localtime),
        ),
        migrations.AlterField(
            model_name='training',
            name='time',
            field=models.TimeField(default=content.models.Training.now_round),
        ),
    ]
