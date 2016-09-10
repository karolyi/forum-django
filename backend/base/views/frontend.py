from base.choices import (
    TOPIC_TYPE_ARCHIVED, TOPIC_TYPE_HIGHLIGHTED, TOPIC_TYPE_NORMAL)
from base.utils.home import collect_topic_page
from django.shortcuts import render


def home(request):
    request_context = {
        'topics_highlighted': collect_topic_page(
            request=request, topic_type=TOPIC_TYPE_HIGHLIGHTED, page_id=1),
        'topics_normal': collect_topic_page(
            request=request, topic_type=TOPIC_TYPE_NORMAL, page_id=1),
        'topics_archived': collect_topic_page(
            request=request, topic_type=TOPIC_TYPE_ARCHIVED, page_id=1),
    }
    return render(request, 'default/base/home.html', request_context)
