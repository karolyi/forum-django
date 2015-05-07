# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20150507_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(editable=False, populate_from=('text_name',), max_length=100, unique=True, blank=True, verbose_name='Topic slug'),
        ),
    ]
