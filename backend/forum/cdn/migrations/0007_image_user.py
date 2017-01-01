# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_auto_20150525_2043'),
        ('cdn', '0006_auto_20150607_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='user',
            field=models.ManyToManyField(to='base.User'),
        ),
    ]
