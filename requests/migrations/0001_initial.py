# Generated by Django 4.2.14 on 2024-08-04 11:44

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Request",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("request_for_date", models.DateTimeField()),
                ("request_start", models.DateTimeField()),
                (
                    "duration_hours",
                    models.FloatField(
                        default=1.0,
                        help_text="مدت زمان درخواست به ساعت",
                        validators=[django.core.validators.MinValueValidator(0.0)],
                    ),
                ),
                ("request_end", models.DateTimeField()),
                ("address", models.TextField()),
                ("for_others", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "در انتظار"),
                            ("ACCEPTED", "پذیرفته شده"),
                            ("REJECTED", "رد شده"),
                            ("COMPLETED", "تکمیل شده"),
                            ("CANCELLED", "لغو شده"),
                            ("NURSING", "پرستاری در حال انجام"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "rate",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(10.0),
                        ],
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("CHILD", "فرزند خردسال"),
                            ("ELDERLY", "والدین کهنسال"),
                        ],
                        default="CHILD",
                        max_length=10,
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="requests",
                        to="accounts.clientprofile",
                    ),
                ),
                (
                    "nurse",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="requests",
                        to="accounts.nurseprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_date"],
            },
        ),
    ]
