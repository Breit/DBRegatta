# Generated by Django 4.0.6 on 2022-08-12 21:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='RaceAssign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race_id', models.BigIntegerField()),
                ('team_id', models.BigIntegerField(blank=True)),
                ('lane', models.CharField(max_length=20)),
                ('time', models.TimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RaceDrawMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race_id', models.BigIntegerField()),
                ('desc', models.CharField(blank=True, max_length=200)),
                ('lane', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=False)),
                ('wait', models.BooleanField(default=False)),
                ('date', models.DateField(default=datetime.date.today)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('company', models.CharField(max_length=200)),
                ('contact', models.CharField(blank=True, max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
            ],
        ),
    ]