# Generated by Django 4.2.14 on 2024-08-18 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_user_otp_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="national_card_image",
            field=models.ImageField(blank=True, null=True, upload_to="national_card"),
        ),
    ]
