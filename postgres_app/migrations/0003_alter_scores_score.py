# Generated by Django 4.1.13 on 2023-11-30 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("postgres_app", "0002_scores_attempts_count_scores_quiz_attempted"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scores",
            name="score",
            field=models.CharField(max_length=20),
        ),
    ]