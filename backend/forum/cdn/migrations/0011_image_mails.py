# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_messaging', '0001_initial'),
        ('forum_cdn', '0010_auto_20151010_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='mails',
            field=models.ManyToManyField(
                verbose_name='In mail', to='forum_messaging.Mail'),
        ),
    ]
