# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_auto_20150525_2038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='time',
            field=models.DateTimeField(verbose_name='Commented at'),
        ),
        migrations.AlterField(
            model_name='edit',
            name='timestamp',
            field=models.DateTimeField(verbose_name='Edit timestamp'),
        ),
    ]
