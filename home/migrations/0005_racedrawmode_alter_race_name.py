# Generated by Django 4.0.6 on 2022-08-08 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_alter_raceassign_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='RaceDrawMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race_id', models.BigIntegerField()),
                ('desc', models.CharField(blank=True, max_length=200)),
                ('lane', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='race',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
