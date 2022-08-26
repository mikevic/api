# Generated by Django 3.1.14 on 2022-06-15 11:36

from django.db import migrations, models

def fill_is_approved(apps, schema_editor):
    """
        For existing Actions, Events and Vendors, if already published then set is_approved to true
    """
    Action = apps.get_model('database', 'Action')
    for instance in Action.objects.filter(is_deleted=False, is_published=True):
        instance.is_approved = True
        instance.save()

    Event = apps.get_model('database', 'Event')
    for instance in Event.objects.filter(is_deleted=False, is_published=True):
        instance.is_approved = True
        instance.save()

    Vendor = apps.get_model('database', 'Vendor')
    for instance in Vendor.objects.filter(is_deleted=False, is_published=True):
        instance.is_approved = True
        instance.save()

class Migration(migrations.Migration):

    dependencies = [
        ('database', '0118_feature_flags'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='is_approved',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='is_approved',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='vendor',
            name='is_approved',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.RunPython(fill_is_approved),

    ]
