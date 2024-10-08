# Generated by Django 4.2.16 on 2024-10-06 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mechanicprofile',
            name='address_latitude',
            field=models.DecimalField(decimal_places=15, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='mechanicprofile',
            name='address_longitude',
            field=models.DecimalField(decimal_places=15, max_digits=20, null=True),
        ),
    ]
