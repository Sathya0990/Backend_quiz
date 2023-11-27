# Generated by Django 4.1.13 on 2023-11-27 07:14

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="courses",
            fields=[
                ("course_id", models.AutoField(primary_key=True, serialize=False)),
                ("course_code", models.IntegerField(unique=True)),
                ("course_name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="teachers",
            fields=[
                ("teacher_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=50)),
                ("email_id", models.EmailField(max_length=254, unique=True)),
                ("password", models.CharField(max_length=50)),
                (
                    "teach_list",
                    models.ManyToManyField(blank=True, to="postgres_app.courses"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="students",
            fields=[
                ("student_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=50)),
                ("email_id", models.EmailField(max_length=254, unique=True)),
                ("password", models.CharField(max_length=50)),
                (
                    "courses_list",
                    models.ManyToManyField(blank=True, to="postgres_app.courses"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="scores",
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
                ("score", models.IntegerField()),
                (
                    "course_id",
                    models.ForeignKey(
                        on_delete=models.Model, to="postgres_app.courses"
                    ),
                ),
                (
                    "student_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="postgres_app.students",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="quizzes",
            fields=[
                ("quiz_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "quiz_content",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.JSONField(), blank=True, null=True, size=None
                    ),
                ),
                ("start_time", models.CharField(max_length=50)),
                ("start_date", models.CharField(max_length=50)),
                ("duration", models.CharField(max_length=50)),
                (
                    "course_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="postgres_app.courses",
                    ),
                ),
                (
                    "teacher_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="postgres_app.teachers",
                    ),
                ),
            ],
        ),
    ]
