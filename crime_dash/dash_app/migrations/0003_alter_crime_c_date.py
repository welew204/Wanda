# Generated by Django 4.2.5 on 2023-09-13 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dash_app", "0002_alter_crime_c_description_alter_crime_c_lat_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="crime",
            name="c_date",
            field=models.DateField(verbose_name="Date"),
        ),
    ]
