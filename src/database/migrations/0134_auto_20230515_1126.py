# Generated by Django 3.1.14 on 2023-05-15 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0133_auto_20230501_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='policies',
            field=models.ManyToManyField(blank=True, related_name='community_policies', to='database.Policy'),
        ),
    ]
