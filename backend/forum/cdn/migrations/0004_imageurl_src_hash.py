# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib

from django.db import migrations, models


def migrate_forward(apps, schema_editor):
    """
    Migrates the orig_src field from Image to ImageUrl table
    """
    ImageUrl = apps.get_model('forum_cdn', 'ImageUrl')
    for image_url in ImageUrl.objects.all():
        src_hash = hashlib.sha512(
            bytearray(image_url.orig_src, 'utf-8')).hexdigest()
        image_url_list = ImageUrl.objects.filter(id=image_url.id)
        image_url_list.update(src_hash=src_hash)


class Migration(migrations.Migration):

    dependencies = [
        ('forum_cdn', '0003_auto_20150525_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageurl', name='src_hash', field=models.CharField(
                max_length=128, verbose_name='SHA512 hash of orig_src'),
            preserve_default=False,
        ),
        migrations.RunPython(
            migrate_forward, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='imageurl', name='src_hash', field=models.CharField(
                verbose_name='SHA512 hash of orig_src', max_length=128,
                unique=True, null=False),
        ),
    ]
