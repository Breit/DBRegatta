# Generated by Django 4.0.6 on 2022-08-15 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_alter_team_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='phone',
            field=models.CharField(blank=True, max_length=25),
        ),
    ]