from rjsmin import jsmin as jsmin_function
from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.tag
def jsmin(parser, token):
    """
    Define a `jsmin` tag that reads until an `endjsmin` tag.
    """
    nodelist = parser.parse(('endjsmin',))
    parser.delete_first_token()
    return JsMin(nodelist)


class JsMin(template.Node):
    """
    Use jsmin to minify the inline JavaScript code.
    """

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        """
        Render the input string.

        If in `DEBUG` mode, don't minify.
        """
        output = self.nodelist.render(context)
        if not settings.DEBUG:
            return jsmin_function(output)
        return output
