# Generated by Django 4.0.6 on 2023-03-27 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_training'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
