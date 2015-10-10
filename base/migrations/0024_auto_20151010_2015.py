# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_settings_friended_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='friended_users',
            field=models.ManyToManyField(related_name='friended_him', to=settings.AUTH_USER_MODEL, verbose_name='Friended users'),
        ),
    ]
