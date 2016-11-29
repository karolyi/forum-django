# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_auto_20151009_2232'),
        ('cdn', '0009_auto_20150704_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='events',
            field=models.ManyToManyField(to='event.Event', verbose_name='In event'),
        ),
        migrations.AlterField(
            model_name='image',
            name='topics',
            field=models.ManyToManyField(to='base.Topic', verbose_name='In topic'),
        ),
        migrations.AlterField(
            model_name='image',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='In user introduction'),
        ),
    ]
