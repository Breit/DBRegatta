# Generated by Django 4.0.6 on 2023-05-26 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0019_training_free_entry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='training',
            name='free_entry',
        ),
        migrations.AddField(
            model_name='team',
            name='nofee',
            field=models.BooleanField(default=False),
        ),
    ]
