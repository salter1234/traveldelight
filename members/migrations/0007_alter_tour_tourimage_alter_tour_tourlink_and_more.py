# Generated by Django 4.2.16 on 2024-11-05 03:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0006_alter_tour_earliergodate_alter_tour_tourspecial_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tour",
            name="tourimage",
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name="tour",
            name="tourlink",
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name="tour",
            name="tourname",
            field=models.CharField(max_length=300, null=True),
        ),
    ]
