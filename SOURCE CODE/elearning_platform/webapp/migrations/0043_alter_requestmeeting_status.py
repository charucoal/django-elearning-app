# Generated by Django 4.2.16 on 2025-02-27 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0042_remove_feedbackforum_parent_feedback_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="requestmeeting",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("accepted", "Accepted"),
                    ("declined", "Declined"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
