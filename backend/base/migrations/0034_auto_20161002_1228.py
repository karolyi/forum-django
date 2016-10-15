# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-02 12:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0033_auto_20160918_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='prev_comment',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='reply_set', to='base.Comment', verbose_name='Replied comment'),
        ),
    ]