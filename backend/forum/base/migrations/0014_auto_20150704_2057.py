# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0013_auto_20150704_1941'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='settings',
            name='inviter',
        ),
        migrations.AddField(
            model_name='settings',
            name='invited_by',
            field=models.ForeignKey(null=True, related_name='invited_by', to=settings.AUTH_USER_MODEL, verbose_name='Invited by', default=None),
        ),
        migrations.AlterField(
            model_name='settings',
            name='ignored_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='List of ignored users', related_name='ignored_users'),
        ),
    ]
