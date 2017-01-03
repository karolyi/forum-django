# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0003_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='todays_comment_count',
        ),
        migrations.AddField(
            model_name='user',
            name='ignored_users',
            field=models.ManyToManyField(verbose_name='List of ignored users', null=None, to='self', related_name='ignored_users_rel_+'),
        ),
        migrations.AddField(
            model_name='user',
            name='inviter',
            field=models.ForeignKey(verbose_name='Invited by', default=None, to='self', null=True),
        ),
    ]
