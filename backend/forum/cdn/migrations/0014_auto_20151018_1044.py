# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_cdn', '0013_auto_20151011_1043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='image',
            name='events',
        ),
        migrations.RemoveField(
            model_name='image',
            name='global_messages',
        ),
        migrations.RemoveField(
            model_name='image',
            name='mails',
        ),
        migrations.RemoveField(
            model_name='image',
            name='project_backers',
        ),
        migrations.RemoveField(
            model_name='image',
            name='projects',
        ),
        migrations.RemoveField(
            model_name='image',
            name='topics',
        ),
        migrations.RemoveField(
            model_name='image',
            name='users',
        ),
    ]
