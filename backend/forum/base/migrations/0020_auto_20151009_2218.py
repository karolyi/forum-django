# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0019_auto_20151009_1914'),
    ]

    operations = [
        migrations.RenameField(
            model_name='settings',
            old_name='introduction_all_html',
            new_name='introduction_html_all',
        ),
        migrations.RenameField(
            model_name='settings',
            old_name='introduction_friends_html',
            new_name='introduction_html_friends',
        ),
        migrations.RenameField(
            model_name='settings',
            old_name='introduction_reg_html',
            new_name='introduction_html_reg',
        ),
        migrations.RenameField(
            model_name='settings',
            old_name='introduction_all_md',
            new_name='introduction_md_all',
        ),
        migrations.RenameField(
            model_name='settings',
            old_name='introduction_friends_md',
            new_name='introduction_md_friends',
        ),
        migrations.RenameField(
            model_name='settings',
            old_name='introduction_reg_md',
            new_name='introduction_md_reg',
        ),
        migrations.RenameField(
            model_name='topic',
            old_name='html_name',
            new_name='name_html',
        ),
        migrations.RenameField(
            model_name='topic',
            old_name='text_name',
            new_name='name_text',
        ),
        migrations.AlterField(
            model_name='topic',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(blank=True, populate_from=('text_name',), unique=True, editable=False, max_length=100, verbose_name='Slug'),
        ),
    ]
