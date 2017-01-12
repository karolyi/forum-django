# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-12 15:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0034_auto_20161002_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='comment_vote_hide_limit',
            field=models.IntegerField(choices=[(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7), (-8, -8), (-9, -9), (-10, -10)], default=-5, verbose_name='Hide comments under this vote value'),
        ),
    ]
