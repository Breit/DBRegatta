# Generated by Django 4.0.6 on 2022-08-14 21:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='date',
            field=models.DateField(blank=True, default=datetime.date.today),
        ),
    ]
