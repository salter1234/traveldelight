# Generated by Django 4.2.16 on 2024-11-05 03:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0002_alter_tour_travelpoint"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tour",
            name="hotel",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
