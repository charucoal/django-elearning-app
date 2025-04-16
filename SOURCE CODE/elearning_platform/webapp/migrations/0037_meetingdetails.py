# Generated by Django 4.2.16 on 2025-02-26 10:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0036_requestmeeting"),
    ]

    operations = [
        migrations.CreateModel(
            name="MeetingDetails",
            fields=[
                ("meeting_id", models.AutoField(primary_key=True, serialize=False)),
                ("start_datetime", models.DateTimeField()),
                ("duration", models.DurationField()),
                (
                    "meeting_status",
                    models.CharField(
                        choices=[
                            ("closed", "Closed"),
                            ("open", "Open"),
                            ("expired", "Expired"),
                        ],
                        default="closed",
                        max_length=20,
                    ),
                ),
                ("password", models.CharField(blank=True, max_length=16, null=True)),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="webapp.requestmeeting",
                    ),
                ),
            ],
        ),
    ]
