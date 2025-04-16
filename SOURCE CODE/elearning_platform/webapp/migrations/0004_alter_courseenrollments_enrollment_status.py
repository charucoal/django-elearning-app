# Generated by Django 4.2.16 on 2025-02-16 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0003_coursedetails_courseenrollments"),
    ]

    operations = [
        migrations.AlterField(
            model_name="courseenrollments",
            name="enrollment_status",
            field=models.CharField(
                choices=[
                    ("enrolled", "Enrolled"),
                    ("unenrolled", "Unenrolled"),
                    ("not_enrolled", "Not Enrolled"),
                    ("removed", "Removed"),
                ],
                default="not_enrolled",
                max_length=20,
            ),
        ),
    ]
