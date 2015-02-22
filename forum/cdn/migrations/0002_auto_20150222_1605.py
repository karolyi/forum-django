# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20150222_1605'),
        ('cdn', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MissingImages',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('src', models.URLField(verbose_name='Original source', max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='images',
            name='comment',
            field=models.ForeignKey(to='base.Comments', default=1, verbose_name='Found in comment', null=None),
            preserve_default=True,
        ),
    ]
