# Generated by Django 4.2.16 on 2025-02-18 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0020_lessondetails_materialupload_assignmentupload_lesson"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assignmentupload",
            name="description",
            field=models.TextField(default="Refer to attached file."),
        ),
    ]
