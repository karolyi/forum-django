# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_event', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='response',
            old_name='response',
            new_name='status',
        ),
    ]
