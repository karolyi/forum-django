# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cdn', '0002_auto_20150222_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='cdn_path',
            field=models.CharField(unique=True, max_length=255, verbose_name='Path in CDN'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='image',
            name='file_hash',
            field=models.CharField(unique=True, max_length=200, verbose_name='File hash'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='image',
            name='orig_src',
            field=models.URLField(db_index=True, max_length=512, verbose_name='Original source'),
            preserve_default=True,
        ),
    ]
