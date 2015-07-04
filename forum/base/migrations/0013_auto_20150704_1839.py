# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20150704_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(blank=True, populate_from=base.models.Settings._get_user_username, editable=False, unique=True, verbose_name='Slug of the user'),
        ),
    ]
