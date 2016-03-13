# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models, connection
from django.conf import settings


def migrate_forward(apps, schema_editor):
    """
    Change the thread_id collation to BINARY.
    """
    cursor = connection.cursor()
    Mail = apps.get_model('messaging', 'Mail')
    # Mail.object.raw
    cursor.execute(
        'ALTER TABLE `%s` MODIFY `%s` varchar(%s) CHARACTER SET utf8 '
        'COLLATE utf8_bin DEFAULT NULL' % (
            Mail._meta.db_table, Mail._meta.get_field('thread_id').column,
            Mail._meta.get_field('thread_id').max_length))


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.AutoField(
                    serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('thread_id', models.CharField(
                    max_length=10, null=True, verbose_name='Thread ID')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True, verbose_name='Created at')),
                ('opened_at', models.DateTimeField(
                    null=True, verbose_name='Read at')),
                ('status', models.PositiveSmallIntegerField(default=0, verbose_name='Status', choices=[
                 (0, 'Unread'), (1, 'Read'), (2, 'Deleted'), (3, 'Replied')])),
                ('is_forwarded', models.BooleanField(
                    default=False, verbose_name='Is forwarded')),
                ('is_retained_sender', models.BooleanField(
                    default=False, verbose_name="Retained in sender's outbox")),
                ('is_retained_recipient', models.BooleanField(
                    default=False, verbose_name="Retained in recipient's outbox")),
                ('content_html', models.TextField(
                    verbose_name='HTML content')),
                ('content_md', models.TextField(
                    verbose_name='Markdown content')),
                ('recipient', models.ForeignKey(related_name='inbox_recipient',
                                                verbose_name='Recipient', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(related_name='inbox_sender',
                                             verbose_name='Sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Mail messages',
                'verbose_name': 'Mail message',
            },
        ),
        migrations.RunPython(
            migrate_forward, reverse_code=migrations.RunPython.noop)
    ]
