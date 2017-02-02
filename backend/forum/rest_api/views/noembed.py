from django.http.response import JsonResponse


def md_parser(request):
    """
    Create a HTML snippet for a given URL of if it's an image, download
    and place it into the CDN, and return a HTML5 image srcset.
    """
    return JsonResponse({'html': '<i>hello world</i>'})
