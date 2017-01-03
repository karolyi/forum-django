# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_cdn', '0014_auto_20151018_1044'),
        ('forum_messaging', '0005_auto_20151010_2101'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalmessage',
            name='images',
            field=models.ManyToManyField(
                to='forum_cdn.Image', verbose_name='Images in this global message'),
        ),
        migrations.AddField(
            model_name='mail',
            name='images',
            field=models.ManyToManyField(
                to='forum_cdn.Image', verbose_name='Images in this mail message'),
        ),
    ]
