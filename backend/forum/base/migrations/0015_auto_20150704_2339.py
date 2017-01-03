# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0014_auto_20150704_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='invited_by',
            field=models.ForeignKey(related_name='invited_user_setting_set', verbose_name='Invited by', null=True, default=None, to=settings.AUTH_USER_MODEL),
        ),
    ]
