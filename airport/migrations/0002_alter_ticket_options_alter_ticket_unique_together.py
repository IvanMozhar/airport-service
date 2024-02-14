# Generated by Django 5.0.2 on 2024-02-14 06:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ticket",
            options={"ordering": ["row", "seat"]},
        ),
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("flight", "row", "seat")},
        ),
    ]