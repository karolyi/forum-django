# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0004_auto_20150507_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(blank=True, unique=True, populate_from=('username',), editable=False, verbose_name='Slug of the user'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='comment_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Comment count'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='last_comment',
            field=models.ForeignKey(to='forum_base.Comment', null=True, on_delete=django.db.models.deletion.SET_NULL, verbose_name='Last comment reference', related_name='last_comment'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='reply_to',
            field=models.ForeignKey(to='forum_base.Topic', null=True, on_delete=django.db.models.deletion.SET_NULL, default=None, verbose_name='Reply to topic goes to'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(blank=True, max_length=100, editable=False, populate_from=('text',), verbose_name='Topic slug'),
        ),
    ]
