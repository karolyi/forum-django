from django.db.models.base import Model

from .query_cache import is_query_prefetched
from .related_field import get_reverse_fk_relations


def remote_fks_exist(obj: Model, ignores: frozenset = frozenset()) -> bool:
    """
    Return `True` if the passed Model instance `obj` is referred in
    its remote `ForeignKey` relations.
    """
    for rel_name in get_reverse_fk_relations(model=obj._meta.model):
        if rel_name in ignores:
            continue
        relation = getattr(obj, rel_name)
        if is_query_prefetched(relation=relation):
            if relation.all():
                return True
        elif relation.exists():
            return True
    return False
