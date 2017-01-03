# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_cdn', '0014_auto_20151018_1044'),
        ('forum_event', '0004_auto_20151010_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='images',
            field=models.ManyToManyField(to='forum_cdn.Image', verbose_name="Images in this event's description"),
        ),
    ]
