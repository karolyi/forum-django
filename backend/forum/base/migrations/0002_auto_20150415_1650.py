# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.backends.mysql.base import DatabaseWrapper


def remove_fk(apps, schema_editor):
    if not isinstance(schema_editor.connection, DatabaseWrapper):
        return
    cursor = schema_editor.connection.cursor()
    Edit = apps.get_model('base', 'Edit')
    table_edit_name = Edit._meta.db_table
    cursor.execute('SELECT DATABASE()')
    db_name = cursor.fetchall()[0][0]
    cursor.execute(
        'SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE'
        ' `TABLE_SCHEMA`=\'%s\' AND `REFERENCED_TABLE_NAME`=\'%s\'' % (
            db_name,
            table_edit_name
        ))
    result = cursor.fetchall()
    if not result:
        return

    Comment = apps.get_model('base', 'Comment')
    table_comment_name = Comment._meta.db_table
    fk_name = result[0][0]
    query = 'ALTER TABLE `%s` DROP FOREIGN KEY `%s`' % (
        table_comment_name,
        fk_name
    )
    cursor.execute(query)


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            remove_fk, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='comment',
            name='edits',
        ),
        migrations.AddField(
            model_name='edit',
            name='comment',
            field=models.ForeignKey(
                to='base.Comment', verbose_name='Edited comment', default=None),
            preserve_default=False,
        ),
    ]
