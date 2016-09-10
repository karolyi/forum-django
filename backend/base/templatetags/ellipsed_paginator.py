from django import template
from django.conf import settings
from django.core.paginator import Page

register = template.Library()


@register.assignment_tag
def get_paginated_list(
        page=None, max_pages=settings.PAGINATOR_MAX_PAGES_TOPICLIST):
    """
    Generate a paginator list with ellipsis.
    """
    # Sanity check
    if type(page) is not Page or page.paginator.count == 0:
        return None
    paginator = page.paginator
    num_pages = paginator.num_pages
    if num_pages == 1:
        return ({
            'number': 1,
            'type': 'number'
        },)
    page_range = max_pages
    if page.number > max_pages:
        # The page is within the shown paginator page amount
        page_range -= 2
    if num_pages < max_pages:
        # The amount of pages is less then the passed max_pages
        page_range = num_pages
    page_number_list = []
    for idx in range(page_range):
        page_number_list.append({
            'number': idx + 1,
            'type': 'number',
        })
    if page.number > max_pages:
        # Append the last two pages
        page_number_list.append({
            'number': page.number,
            'type': 'number'
        })
        page_number_list.append({
            'number': paginator.num_pages,
            'type': 'number'
        })
    return page_number_list
