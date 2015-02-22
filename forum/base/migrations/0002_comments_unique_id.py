# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='unique_id',
            field=models.CharField(
                default=1, verbose_name='Obsolete unique ID', max_length=20, unique=True),
            preserve_default=True,
        ),
    ]
