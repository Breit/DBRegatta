# Generated by Django 4.0.6 on 2022-08-14 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_alter_team_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='date',
            field=models.DateField(blank=True),
        ),
    ]
