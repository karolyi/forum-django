# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_messaging', '0004_globalmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalmessage',
            name='created_at',
            field=models.DateTimeField(verbose_name='Created at', auto_now_add=True),
        ),
    ]
