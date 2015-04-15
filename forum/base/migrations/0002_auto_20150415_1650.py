# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='edits',
        ),
        migrations.AddField(
            model_name='edit',
            name='comment',
            field=models.ForeignKey(to='base.Comment', verbose_name='Edited comment', default=None),
            preserve_default=False,
        ),
    ]
