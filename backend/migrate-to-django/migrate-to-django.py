#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: comment edits

# This needs to be imported first: sets up django
from setup import do_setup

import datetime
import logging

from django.db import transaction

import maintenance
# Self-written modules need to be imported after initializing
import variables
from comment_bookmark_parser import parse_bookmarks
from crowfunding_parser import parse_crowdfunding
from messageparser import parse_global_messages, parse_messaging
from poll_parser import parse_polls

logger = logging.getLogger(__name__)


def main():
    transaction.set_autocommit(False)
    maintenance.cdn_maintenance()
    maintenance.empty_django_db()
    maintenance.parse_users()
    maintenance.parse_topics()
    transaction.commit()

    parse_polls()
    transaction.commit()

    maintenance.parse_events()
    maintenance.parse_event_responses()
    transaction.commit()

    parse_crowdfunding()
    transaction.commit()

    parse_messaging()
    transaction.commit()

    parse_global_messages()
    transaction.commit()

    maintenance.parse_comments()
    transaction.commit()

    maintenance.update_last_comments()

    parse_bookmarks()
    transaction.commit()

    maintenance.parse_comment_votes()
    transaction.commit()

    # maintenance.parse_bookmarks()
    # file_handler.delete_unused_cdn_files()
    logger.info(
        '======================== Finished at: %s', datetime.datetime.now())
    logger.info(
        'SUCCESSFULLY_DOWNLOADED: %s, MISSING: %s, '
        'ALREADY_DOWNLOADED: %s, ALREADY_MISSING: %s, '
        'CDN_NO_MODEL: %s, CDN_NO_FILE: %s',
        variables.SUCCESSFULLY_DOWNLOADED, variables.MISSING_IMAGE_COUNT,
        variables.ALREADY_DOWNLOADED_IMAGE_COUNT,
        variables.ALREADY_MISSING_IMAGE_COUNT,
        variables.CDN_NO_MODEL, variables.CDN_NO_FILE)


do_setup()
main()
