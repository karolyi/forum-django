# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='is_retained_recipient',
            field=models.BooleanField(verbose_name="Retained in recipient's inbox", default=False),
        ),
        migrations.AlterField(
            model_name='mail',
            name='status',
            field=models.PositiveSmallIntegerField(verbose_name='Status', default=1, choices=[(1, 'Unread'), (2, 'Read'), (3, 'Deleted'), (4, 'Replied')]),
        ),
    ]
