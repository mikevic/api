# Generated by Django 3.1.14 on 2023-07-10 10:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0135_deviceprofile_accepted_cookies'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deviceprofile',
            old_name='accepted_cookies',
            new_name='has_accepted_cookies',
        ),
    ]
