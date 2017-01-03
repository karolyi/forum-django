# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0010_auto_20150525_2043'),
        ('forum_cdn', '0005_auto_20150525_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='topic',
            field=models.ManyToManyField(to='forum_base.Topic'),
        ),
        migrations.AlterField(
            model_name='image',
            name='comment',
            field=models.ManyToManyField(verbose_name='Found in comment', to='forum_base.Comment'),
        ),
    ]
