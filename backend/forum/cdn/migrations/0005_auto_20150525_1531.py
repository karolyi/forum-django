# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_cdn', '0004_imageurl_src_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='file_hash',
            field=models.CharField(max_length=128, unique=True, verbose_name='File SHA512 hash'),
        ),
    ]
