# Generated by Django 4.0.6 on 2023-09-01 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0024_alter_team_category_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='category_id',
            field=models.BigIntegerField(blank=True, default=None, null=True),
        ),
    ]
