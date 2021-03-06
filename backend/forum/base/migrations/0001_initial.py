# Generated by Django 2.2.9 on 2019-12-23 12:13

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('forum_cdn', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('slug', django_extensions.db.fields.AutoSlugField(blank=True, editable=False, populate_from='username', unique=True, verbose_name='Slug of the user')),
                ('last_global_read', models.PositiveIntegerField(default=0, verbose_name='Last global message ID read')),
                ('received_comment_vote_sum', models.IntegerField(default=0, verbose_name='Summary received votes value on comments')),
                ('received_comment_vote_count', models.PositiveIntegerField(default=0, verbose_name='Summary received votes count on comments')),
                ('comment_vote_hide_limit', models.IntegerField(choices=[(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7), (-8, -8), (-9, -9), (-10, -10)], default=-5, help_text='If a comment gets voted down under the selected value here, it gets completely hidden.', verbose_name='Hide comments under this vote value')),
                ('quote', models.CharField(blank=True, help_text='Quote (visible in the tooltip of the username)', max_length=256, verbose_name='Chosen quote')),
                ('max_comments_per_day', models.IntegerField(default=-1, verbose_name='Maximum allowed comments per day')),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='Comment count')),
                ('invitations_today', models.PositiveIntegerField(default=0, verbose_name='Sent invitations today')),
                ('invitations_success', models.PositiveIntegerField(default=0, verbose_name='Successful invitations')),
                ('pw_reminders_today', models.PositiveIntegerField(default=0, verbose_name='Password reminders sent today')),
                ('used_skin', models.CharField(default='default', max_length=256, verbose_name='Used skin name')),
                ('introduction_md_all', models.TextField(default='', help_text='Introduction in Markdown format (visible for everyone)', verbose_name='Introduction for everybody (MD)')),
                ('introduction_md_reg', models.TextField(default='', help_text='Introduction in Markdown format (visible for registered users only)', verbose_name='Introduction for registered users (MD)')),
                ('introduction_md_friends', models.TextField(default='', help_text='Introduction in Markdown format (visible only for users marked as friends)', verbose_name='Introduction for friended users (MD)')),
                ('introduction_html_all', models.TextField(default='', help_text='Introduction in HTML format (visible for everyone)', verbose_name='Introduction for everybody (HTML)')),
                ('introduction_html_reg', models.TextField(default='', help_text='Introduction in HTML format (visible for registered users only)', verbose_name='Introduction for registered users (HTML)')),
                ('introduction_html_friends', models.TextField(default='', help_text='Introduction in HTML format (visible only for users marked as friends)', verbose_name='Introduction for friended users (HTML)')),
                ('picture_emails', models.CharField(default='', max_length=256, verbose_name='Email addresses used for image upload separated with semicolons (;)')),
                ('uses_auto_bookmarks', models.BooleanField(default=False, help_text='When checked, the previously set bookmarks will automatically update to the newest seen comment in the topic pages as they are listed.', verbose_name='Use automatic bookmark placement')),
                ('mails_own_topic_comments', models.BooleanField(default=False, help_text='Receive email alerts if someone posts a comment in a created topic.', verbose_name='Receive mails from comments in own topic')),
                ('mails_replies_topic', models.BooleanField(default=True, help_text='Receive email alerts from replies to posted comments.', verbose_name='Receive mails from comment replies')),
                ('mails_moderation_topic', models.BooleanField(default=True, help_text='Receive emails when an administrator takes a moderation action (e.g. edit, deletion, move) on the a posted comment.', verbose_name='Receive mails from moderation')),
                ('mails_messages', models.BooleanField(default=True, help_text='Receive email alerts when a new private message arrives.', verbose_name='Receive mails from messages')),
                ('show_replies_comment', models.BooleanField(default=True, verbose_name='Show replies on comments')),
                ('show_relations', models.BooleanField(default=True, verbose_name='Show user relations')),
                ('is_banned', models.BooleanField(default=False, verbose_name='User is banned')),
                ('separate_bookmarked_topics', models.BooleanField(default=True, help_text='Split the normal topic view to topics with set bookmarks and topics with none set.', verbose_name='Show bookmarked topics separated')),
                ('show_outsiders', models.BooleanField(default=True, verbose_name='Show not-logged-in users')),
                ('has_chat_enabled', models.BooleanField(default=True, help_text='Show the chat on the main page when logged in.', verbose_name='Enable chat')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Is approved by admins')),
                ('expand_archived', models.BooleanField(default=False, help_text="Don't hide archived topics on the main page.", verbose_name='Expand archived topics')),
                ('friended_users', models.ManyToManyField(blank=True, help_text='The users who will see the part of the profile which is only visible for friended users.', related_name='friended_by', to=settings.AUTH_USER_MODEL, verbose_name='Friended users')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('ignored_users', models.ManyToManyField(blank=True, help_text="An ignored user's posts are invisible when added here.", related_name='ignored_by', to=settings.AUTH_USER_MODEL, verbose_name='List of ignored users')),
                ('images', models.ManyToManyField(to='forum_cdn.Image', verbose_name="Images in this user's descriptions")),
                ('invited_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invited_user_setting_set', to=settings.AUTH_USER_MODEL, verbose_name='Invited by')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User setting',
                'verbose_name_plural': 'User settings',
                'ordering': ['username'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(verbose_name='Commented at')),
                ('number', models.PositiveIntegerField(verbose_name='Comment number in topic')),
                ('voting_value', models.SmallIntegerField(verbose_name='Value of up/downvotes')),
                ('content_md', models.TextField(verbose_name='Markdown content')),
                ('content_html', models.TextField(verbose_name='HTML content')),
                ('host', models.CharField(max_length=256, verbose_name='Host of the commenter (old)')),
                ('ip', models.GenericIPAddressField(verbose_name='IP of the commenter')),
                ('unique_id', models.CharField(default=0, max_length=20, unique=True, verbose_name='Obsolete unique ID')),
                ('images', models.ManyToManyField(to='forum_cdn.Image', verbose_name='Images in this comment')),
            ],
            options={
                'ordering': ('-time',),
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', django_extensions.db.fields.AutoSlugField(blank=True, editable=False, max_length=100, populate_from=('name_text',), unique=True, verbose_name='Slug')),
                ('name_html', models.CharField(max_length=256, verbose_name='HTML name')),
                ('name_text', models.CharField(max_length=256, verbose_name='Text name')),
                ('is_enabled', models.BooleanField(default=False, verbose_name='Is enabled')),
                ('is_staff_only', models.BooleanField(default=False, verbose_name='Is staff only')),
                ('is_voting_enabled', models.BooleanField(default=True, verbose_name='Is voting enabled')),
                ('type', models.CharField(choices=[('normal', 'Normal'), ('archived', 'Archived'), ('highlighted', 'Highlighted')], default='normal', max_length=20, verbose_name='Topic type')),
                ('truncate_at', models.SmallIntegerField(null=True, verbose_name='Max comment number to keep')),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='Comment count')),
                ('description', models.TextField(verbose_name='Description')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('images', models.ManyToManyField(to='forum_cdn.Image', verbose_name='Images in this topic description')),
                ('last_comment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_comment', to='forum_base.Comment', verbose_name='Last comment reference')),
                ('reply_to', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forum_base.Topic', verbose_name='Reply to topic goes to')),
            ],
            options={
                'ordering': ['-last_comment__time', 'name_text'],
            },
        ),
        migrations.CreateModel(
            name='IntroductionModification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote', models.CharField(blank=True, help_text='Quote (visible in the tooltip of the username)', max_length=256, verbose_name='Chosen quote')),
                ('introduction_md_all', models.TextField(help_text='Introduction in Markdown format (visible for everyone)', verbose_name='Introduction for everybody (MD)')),
                ('introduction_md_reg', models.TextField(help_text='Introduction in Markdown format (visible for registered users only)', verbose_name='Introduction for registered users (MD)')),
                ('introduction_md_friends', models.TextField(help_text='Introduction in Markdown format (visible only for users marked as friends)', verbose_name='Introduction for friended users (MD)')),
                ('images', models.ManyToManyField(to='forum_cdn.Image', verbose_name="Images in this user's descriptions")),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Respective user')),
            ],
            options={
                'verbose_name': 'Settings modification',
                'verbose_name_plural': 'Settings modifications',
            },
        ),
        migrations.CreateModel(
            name='Edit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Edit timestamp')),
                ('reason', models.CharField(default='', max_length=50, verbose_name='Reason for editing')),
                ('diff', models.TextField(verbose_name='Diff of the previous version')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum_base.Comment', verbose_name='Edited comment')),
                ('edited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Edited by')),
                ('images', models.ManyToManyField(to='forum_cdn.Image', verbose_name='Images in this edit')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='moved_from',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='moved_from', to='forum_base.Topic', verbose_name='Moved from'),
        ),
        migrations.AddField(
            model_name='comment',
            name='prev_comment',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='reply_set', to='forum_base.Comment', verbose_name='Replied comment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum_base.Topic', verbose_name='Topic'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='The commenter user'),
        ),
        migrations.CreateModel(
            name='CommentBookmark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated_at', models.DateTimeField(auto_now=True, verbose_name='Last updated at')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum_base.Comment', verbose_name='Comment')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum_base.Topic', verbose_name='Topic')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Comment bookmark',
                'verbose_name_plural': 'Comment bookmarks',
                'unique_together': {('user', 'topic')},
            },
        ),
        migrations.AlterIndexTogether(
            name='comment',
            index_together={('topic', 'time')},
        ),
    ]
