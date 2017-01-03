# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0025_auto_20151010_2016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edit',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Edit timestamp'),
        ),
    ]
