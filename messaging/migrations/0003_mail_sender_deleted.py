# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0002_auto_20151010_1853'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail',
            name='sender_deleted',
            field=models.BooleanField(default=False, verbose_name='Sender deleted it in outbox'),
        ),
    ]
