# Generated by Django 4.2.16 on 2024-10-02 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_mechanicprofile_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mechanicprofile',
            name='years_of_experience',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
