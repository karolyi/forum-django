# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_auto_20150704_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(unique=True, editable=False, verbose_name='Slug of the user', blank=True, populate_from='_get_user_username'),
        ),
    ]
