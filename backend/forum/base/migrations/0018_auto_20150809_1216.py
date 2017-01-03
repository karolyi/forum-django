# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0017_comment_content_md'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='content',
            new_name='content_html'
        ),
        migrations.AlterField(
            model_name='comment', name='content_html',
            field=models.TextField(
                verbose_name='HTML content'))
    ]
