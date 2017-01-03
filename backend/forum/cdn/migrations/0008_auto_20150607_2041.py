# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_cdn', '0007_image_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='comment',
            new_name='comments',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='topic',
            new_name='topics',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='user',
            new_name='users',
        ),
    ]
