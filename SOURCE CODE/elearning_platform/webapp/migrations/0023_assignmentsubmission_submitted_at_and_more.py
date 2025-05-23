# Generated by Django 4.2.16 on 2025-02-18 06:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0022_alter_assignmentupload_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="assignmentsubmission",
            name="submitted_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="assignmentupload",
            name="lesson",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assignments",
                to="webapp.lessondetails",
            ),
        ),
    ]
