# Generated by Django 2.1.7 on 2019-03-24 02:14

import core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dscan', '0003_dscan_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dscan',
            name='key',
            field=models.CharField(default=core.utils.generate_key, max_length=80, unique=True),
        ),
    ]