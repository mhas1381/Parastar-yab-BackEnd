# Generated by Django 4.2.14 on 2024-08-19 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0003_alter_request_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('PENDING', 'در انتظار'), ('ACCEPTED', 'پذیرفته شده'), ('REJECTED', 'رد شده'), ('COMPLETED', 'تکمیل شده'), ('CANCELLED', 'لغو شده'), ('CLINET_CONFIRMATION', 'انتظار برای تایید متقاضی'), ('NURSING', 'پرستاری در حال انجام')], default='PENDING', max_length=20),
        ),
    ]
