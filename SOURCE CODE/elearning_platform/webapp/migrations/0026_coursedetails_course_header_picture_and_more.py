# Generated by Django 4.2.16 on 2025-02-18 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0025_rename_createdat_userinfo_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="coursedetails",
            name="course_header_picture",
            field=models.ImageField(
                blank=True,
                default="course_pictures/header/default.png",
                null=True,
                upload_to="course_pictures/header",
            ),
        ),
        migrations.AddField(
            model_name="coursedetails",
            name="course_thumbnail_picture",
            field=models.ImageField(
                blank=True,
                default="course_pictures/thumbnail/default.png",
                null=True,
                upload_to="course_pictures/thumbnail",
            ),
        ),
    ]
