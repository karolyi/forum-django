# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
        ('cdn', '0010_auto_20151010_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='mails',
            field=models.ManyToManyField(verbose_name='In mail', to='messaging.Mail'),
        ),
    ]
