"""
    This here is an utterly ugly hack to get django-pipeline and
    django-require to function together. Since both wants to override
    STATICFILES_STORAGE (thus overriding each others functionality),
    we will have to wire them together in the right order.

    So this is what happens here.
"""

from pipeline.storage import PipelineMixin
from require.storage import OptimizedFilesMixin
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class ForumStorage(
        PipelineMixin, OptimizedFilesMixin, ManifestStaticFilesStorage):
    pass
