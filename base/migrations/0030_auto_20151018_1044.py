# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdn', '0014_auto_20151018_1044'),
        ('base', '0029_auto_20151011_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='images',
            field=models.ManyToManyField(to='cdn.Image', verbose_name='Images in this comment'),
        ),
        migrations.AddField(
            model_name='edit',
            name='images',
            field=models.ManyToManyField(to='cdn.Image', verbose_name='Images in this edit'),
        ),
        migrations.AddField(
            model_name='settings',
            name='images',
            field=models.ManyToManyField(to='cdn.Image', verbose_name="Images in this user's descriptions"),
        ),
        migrations.AddField(
            model_name='topic',
            name='images',
            field=models.ManyToManyField(to='cdn.Image', verbose_name='Images in this topic description'),
        ),
    ]
