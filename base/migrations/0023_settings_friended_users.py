# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0022_auto_20151010_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='friended_users',
            field=models.ManyToManyField(related_name='_friended_users_+', verbose_name='Friended users', to='base.Settings'),
        ),
    ]
