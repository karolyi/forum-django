from forum.utils.model_cache import ModelCacheBase

from ..models import Comment, Topic, User


class TopicCache(ModelCacheBase):
    'Model cache for `Topic`.'
    model = Topic
    cache_getter = Topic.objects.get
    cache_updater = Topic.objects.filter


class CommentCache(ModelCacheBase):
    'Model cache for `Comment`.'
    model = Comment
    cache_getter = Comment.objects.get
    cache_updater = Comment.objects.filter


class UserCache(ModelCacheBase):
    'Model cache for `User`.'
    model = User
    cache_getter = User.objects.get
    cache_updater = User.objects.filter
