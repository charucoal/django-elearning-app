# Generated by Django 4.2.16 on 2025-02-17 14:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("webapp", "0006_notification_created_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="Assignment",
            fields=[
                ("assign_id", models.AutoField(primary_key=True, serialize=False)),
                ("upload_file", models.FileField(null=True, upload_to="assignments/")),
                ("deadline", models.DateTimeField(null=True)),
                (
                    "course",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="webapp.coursedetails",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UploadAssignment",
            fields=[
                ("upload_id", models.AutoField(primary_key=True, serialize=False)),
                ("upload_file", models.FileField(upload_to="uploaded_assignments/")),
                (
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="webapp.assignment",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_submissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
