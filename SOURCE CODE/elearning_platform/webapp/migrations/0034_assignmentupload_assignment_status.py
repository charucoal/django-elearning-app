# Generated by Django 4.2.16 on 2025-02-25 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0033_remove_assignmentsubmission_submitted_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="assignmentupload",
            name="assignment_status",
            field=models.BooleanField(default=True),
        ),
    ]
