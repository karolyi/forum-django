# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdn', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='missingimage',
            name='src',
            field=models.URLField(
                unique=True, db_index=True, max_length=191,
                verbose_name='Original source'),
        ),
    ]
