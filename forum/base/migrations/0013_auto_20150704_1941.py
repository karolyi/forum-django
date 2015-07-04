# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20150704_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(editable=False, blank=True, verbose_name='Slug of the user', unique=True, populate_from='user'),
        ),
    ]
