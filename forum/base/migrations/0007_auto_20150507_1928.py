# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20150507_1822'),
    ]

    operations = [
        migrations.RenameField(
            model_name='topic',
            old_name='html',
            new_name='html_name',
        ),
        migrations.RenameField(
            model_name='topic',
            old_name='text',
            new_name='text_name',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='last_updated',
        ),
        migrations.AddField(
            model_name='topic',
            name='type',
            field=models.CharField(max_length=20, verbose_name='Topic type', default='normal', choices=[('normal', 'Normal'), ('archived', 'Archived'), ('highlighted', 'Highlighted')]),
        ),
    ]
