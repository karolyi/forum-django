# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_auto_20151010_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='ignored_users',
            field=models.ManyToManyField(verbose_name='List of ignored users', to=settings.AUTH_USER_MODEL, related_name='ignored_him'),
        ),
    ]
