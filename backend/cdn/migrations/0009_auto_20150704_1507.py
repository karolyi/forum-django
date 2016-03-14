# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cdn', '0008_auto_20150607_2041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]