# Generated by Django 5.2.1 on 2025-05-19 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_alter_user_address_alter_user_bio_alter_user_city_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="dob",
            field=models.DateField(blank=True, null=True),
        ),
    ]
