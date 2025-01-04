# Generated by Django 5.1.2 on 2024-12-14 18:07

import phonenumber_field.modelfields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="backup_phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True,
                help_text="Enter your phone number starting with the country code (e.g., +647...).",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter your phone number starting with the country code (e.g., +647...).",
                max_length=128,
                region=None,
                unique=True,
            ),
        ),
    ]
