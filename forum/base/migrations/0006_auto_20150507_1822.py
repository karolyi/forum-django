# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20150507_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(populate_from=('text',), unique=True, verbose_name='Topic slug', max_length=100, blank=True, editable=False),
        ),
    ]
