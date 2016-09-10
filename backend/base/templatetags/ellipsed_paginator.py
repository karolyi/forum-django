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
        # Early exit, only one page
        return ({
            'number': 1,
            'type': 'number'
        },)
    page_range = max_pages
    if num_pages > max_pages:
        # The page is NOT within the shown paginator page amount
        page_range -= 1
        if page.number > page_range:
            # The current page cannot be shown amongst one of the the
            # pages, make a place for it
            page_range -= 1
    page_number_list = []
    for idx in range(page_range):
        page_number_list.append({
            'number': idx + 1,
            'type': 'number',
        })
    if page.number > page_range:
        # Append the current page
        page_number_list.append({
            'number': page.number,
            'type': 'number'
        })
    if num_pages > max_pages:
        # Append the last last page
        page_number_list.append({
            'number': paginator.num_pages,
            'type': 'number'
        })
    return page_number_list
