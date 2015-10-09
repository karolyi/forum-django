# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0015_auto_20150704_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='edit',
            name='edited_by',
            field=models.ForeignKey(verbose_name='Edited by', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='edit',
            name='reason',
            field=models.CharField(verbose_name='Reason for editing', max_length=50, default=''),
        ),
    ]
