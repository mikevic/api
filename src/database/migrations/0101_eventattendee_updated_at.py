# Generated by Django 3.1.12 on 2021-08-19 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0100_auto_20210819_1745'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventattendee',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
