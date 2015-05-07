# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20150507_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='inviter',
            field=models.ForeignKey(null=True, to='base.User', default=None, verbose_name='Invited by', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
