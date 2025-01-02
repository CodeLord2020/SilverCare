# Generated by Django 5.1.2 on 2024-12-29 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eldertasks", "0002_taskmedia"),
    ]

    operations = [
        migrations.AlterField(
            model_name="taskapplication",
            name="status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Accepted", "Accepted"),
                    ("Rejected", "Rejected"),
                    ("Withdrawn", "Withdrawn"),
                    ("Completed", "Completed"),
                ],
                default="Pending",
                max_length=20,
            ),
        ),
    ]