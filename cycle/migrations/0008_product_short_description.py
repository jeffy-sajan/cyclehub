# Generated by Django 5.0.6 on 2024-11-14 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cycle', '0007_userprofile_address_userprofile_phone_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='short_description',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
