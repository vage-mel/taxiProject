# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-11-02 09:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('your_taxi', '0003_auto_20170427_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=10, verbose_name='Телефон'),
        ),
    ]
