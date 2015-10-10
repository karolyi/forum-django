# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('event', '0003_response_last_modified'),
    ]

    operations = [
        migrations.RenameModel('Response', 'EventResponse'),
        migrations.AlterModelOptions(
            name='eventresponse',
            options={'verbose_name': 'Event response',
                     'verbose_name_plural': 'Event responses'},
        ),
    ]
