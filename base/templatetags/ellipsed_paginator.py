from django import template
from django.conf import settings
from django.core.paginator import Page

register = template.Library()


@register.assignment_tag
def get_paginated_list(
        page=None, adjacent_pages=settings.PAGINATOR_ADJACENT_PAGES):
    """
    Generate a paginator list with ellipsis.
    """
    # Sanity check
    if type(page) is not Page or page.paginator.count == 0:
        return None
    paginator = page.paginator
    num_pages = paginator.num_pages
    if num_pages == 1:
        return (1,)
    start_page = max(page.number - adjacent_pages, 1)
    end_page = min(page.number + adjacent_pages, num_pages)
    print(start_page, end_page)
    page_number_list = []
    page_number_list.extend((
        x for x in range(start_page, end_page + 1)))

    if 2 not in page_number_list:
        page_number_list.insert(0, 2)
        page_number_list.insert(0, 1)

    if num_pages - 1 not in page_number_list:
        page_number_list.extend((num_pages - 1, num_pages))

    return page_number_list
