# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_auto_20150808_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='content_md',
            field=models.TextField(verbose_name='Markdown content', default=''),
            preserve_default=False,
        ),
    ]
