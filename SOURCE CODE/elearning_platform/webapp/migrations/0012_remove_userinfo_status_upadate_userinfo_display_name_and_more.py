# Generated by Django 4.2.16 on 2025-02-17 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0011_userinfo_status_upadate"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userinfo",
            name="status_upadate",
        ),
        migrations.AddField(
            model_name="userinfo",
            name="display_name",
            field=models.CharField(
                default=models.CharField(max_length=255), max_length=255
            ),
        ),
        migrations.AddField(
            model_name="userinfo",
            name="display_status",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="userinfo",
            name="status_update",
            field=models.TextField(default="Hello! I'm on Voyage!"),
        ),
    ]
