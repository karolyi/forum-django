# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cdn', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='orig_src',
            field=models.URLField(max_length=512, verbose_name='Original source'),
            preserve_default=True,
        ),
    ]
