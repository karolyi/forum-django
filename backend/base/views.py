from django.shortcuts import render
from base.utils.home import collect_topics


def home(request):
    topics_highlighted, topics_normal = collect_topics(request)
    request_context = {
        'topics_highlighted': topics_highlighted,
        'topics_normal': topics_normal
    }
    return render(request, 'default/base/home.html', request_context)
