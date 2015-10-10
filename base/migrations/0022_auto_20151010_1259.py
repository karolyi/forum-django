# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_auto_20151009_2240'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='is_disabled',
        ),
        migrations.AddField(
            model_name='topic',
            name='is_enabled',
            field=models.BooleanField(default=False, verbose_name='Is topic enabled'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='picture_emails',
            field=models.CharField(max_length=256, verbose_name='Email addresses used for image upload separated with semicolons (;)'),
        ),
    ]
