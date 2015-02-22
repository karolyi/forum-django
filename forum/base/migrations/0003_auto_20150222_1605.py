# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_comments_unique_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='unique_id',
            field=models.CharField(unique=True, verbose_name='Obsolete unique ID', default=0, max_length=20),
            preserve_default=True,
        ),
    ]
