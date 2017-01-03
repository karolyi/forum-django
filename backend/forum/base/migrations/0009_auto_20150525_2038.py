# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0008_auto_20150507_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='time',
            field=models.DateTimeField(verbose_name='Commented at', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='edit',
            name='timestamp',
            field=models.DateTimeField(verbose_name='Edit timestamp', auto_now_add=True),
        ),
    ]
