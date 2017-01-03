# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_event', '0002_auto_20151009_2232'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now, verbose_name='Last modified at'),
            preserve_default=False,
        ),
    ]
