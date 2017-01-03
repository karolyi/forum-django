# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0018_auto_20150809_1216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='settings',
            name='introduction_all',
        ),
        migrations.RemoveField(
            model_name='settings',
            name='introduction_friends',
        ),
        migrations.RemoveField(
            model_name='settings',
            name='introduction_reg',
        ),
        migrations.AddField(
            model_name='settings',
            name='introduction_all_html',
            field=models.TextField(verbose_name='Introduction visible for everybody (HTML)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='settings',
            name='introduction_all_md',
            field=models.TextField(verbose_name='Introduction visible for everybody (Markdown)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='settings',
            name='introduction_friends_html',
            field=models.TextField(verbose_name='Introduction visible for friended users (HTML)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='settings',
            name='introduction_friends_md',
            field=models.TextField(verbose_name='Introduction visible for friended users (Markdown)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='settings',
            name='introduction_reg_html',
            field=models.TextField(verbose_name='Introduction visible for registered users (HTML)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='settings',
            name='introduction_reg_md',
            field=models.TextField(verbose_name='Introduction visible for registered users (Markdown)', default=''),
            preserve_default=False,
        ),
    ]
