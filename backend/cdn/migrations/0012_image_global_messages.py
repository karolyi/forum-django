# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0005_auto_20151010_2101'),
        ('cdn', '0011_image_mails'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='global_messages',
            field=models.ManyToManyField(verbose_name='In global message', to='messaging.GlobalMessage'),
        ),
    ]
