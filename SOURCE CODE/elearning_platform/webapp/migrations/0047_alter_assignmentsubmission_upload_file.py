# Generated by Django 4.2.16 on 2025-03-08 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0046_alter_assignmentupload_deadline"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assignmentsubmission",
            name="upload_file",
            field=models.FileField(null=True, upload_to="uploaded_assignments/"),
        ),
    ]
