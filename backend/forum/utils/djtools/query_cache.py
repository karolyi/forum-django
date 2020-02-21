from typing import Iterable, Optional

from django import VERSION
from django.db.models.base import Model
from django.db.models.fields.related import ManyToManyField
from django.db.models.fields.reverse_related import ManyToOneRel
from django.db.models.manager import Manager
from django.db.models.query import QuerySet


def invalidate_onetomany(objs: Iterable[Model], prefetch_keys: Iterable[str]):
    """
    Invalidate one-to-many caches. These are remote `ForeignKey` and
    `ManyToManyField` fields fetched with `prefetch_related()`.
    """
    if VERSION[0] == 1 or VERSION[0] == 2:
        for obj in objs:
            if not hasattr(obj, '_prefetched_objects_cache'):
                continue
            for key in prefetch_keys:
                if key not in obj._prefetched_objects_cache:
                    continue
                del obj._prefetched_objects_cache[key]


def invalidate_manytoone(objs: Iterable[Model], field_names: Iterable[str]):
    """
    Invalidate many-to-one caches. These are `ForeignKey` and
    `OneToOneField` fields fetched with `select_related()` or
    `prefetch_related()`.
    """
    if VERSION[0] == 1:
        for obj in objs:
            for field_name in field_names:
                if not is_fk_cached(obj=obj, field_name=field_name):
                    continue
                del obj.__dict__[f'_{field_name}_cache']
    elif VERSION[0] == 2:
        for obj in objs:
            for field_name in field_names:
                if not is_fk_cached(obj=obj, field_name=field_name):
                    continue
                del obj._state.fields_cache[field_name]


def get_prefetch_cache_key(relation: Manager) -> str:
    'Return a key used in the prefetched cache for a relation.'
    try:
        # Works on ManyToMany
        return relation.prefetch_cache_name
    except AttributeError:
        # Is a ForeignKey (OneToMany)
        rel_field = relation.field.remote_field  # type: ManyToOneRel
        if rel_field.related_name:
            return rel_field.related_name
        if VERSION[0] == 1:
            return rel_field.name
        elif VERSION[0] == 2:
            return f'{rel_field.name}_set'


def init_prefetch_cache(obj: Model):
    'Init a prefetch cache on the model.'
    if VERSION[0] == 1 or VERSION[0] == 2:
        if hasattr(obj, '_prefetched_objects_cache'):
            return
        obj._prefetched_objects_cache = {}


def is_query_prefetched(relation: Manager) -> bool:
    'Return `True` if the relation is prefetched.'
    if VERSION[0] == 1 or VERSION[0] == 2:
        obj = relation.instance
        if not hasattr(obj, '_prefetched_objects_cache'):
            return False
        prefetch_cache_key = get_prefetch_cache_key(relation=relation)
        return prefetch_cache_key in obj._prefetched_objects_cache
    return False


def set_prefetch_cache(
        relation: Manager, queryset: QuerySet, override: bool = True):
    'Set prefetch cache on a `Model` for a relation.'
    if is_query_prefetched(relation=relation) and not override:
        return
    obj = relation.instance
    init_prefetch_cache(obj=obj)
    if VERSION[0] == 1 or VERSION[0] == 2:
        key = get_prefetch_cache_key(relation=relation)
        obj._prefetched_objects_cache[key] = queryset


def is_queryresult_loaded(qs: QuerySet) -> bool:
    'Return `True` if the query is loaded, `False` otherwise.'
    if VERSION[0] == 1 or VERSION[0] == 2:
        return qs._result_cache is not None
    return False


def set_queryresult(qs: QuerySet, result: list, override: bool = True):
    'Set result on a previously setup query.'
    if VERSION[0] == 1 or VERSION[0] == 2:
        if override or not is_queryresult_loaded(qs=qs):
            qs._result_cache = result


def get_queryresult(qs: QuerySet) -> Optional[list]:
    'Return the cached query result of the passed `QuerySet`.'
    if VERSION[0] == 1 or VERSION[0] == 2:
        return qs._result_cache


def is_fk_cached(obj: Model, field_name: str) -> bool:
    'Return `True` if the `ForeignKey` field on the object is cached.'
    if VERSION[0] == 1:
        return hasattr(obj, f'_{field_name}_cache')
    elif VERSION[0] == 2:
        if getattr(obj, '_state', None) is None or \
                getattr(obj._state, 'fields_cache', None) is None:
            return False
        return field_name in obj._state.fields_cache
    return False


def set_fk_cache(
        obj: Model, field_name: str, value: Model, override: bool = True):
    """
    Set a cache on the `obj` for a `ForeignKey` field, override when
    requested.
    """
    if not override and is_fk_cached(obj=obj, field_name=field_name):
        return
    if VERSION[0] == 1:
        setattr(obj, f'_{field_name}_cache', value)
    elif VERSION[0] == 2:
        if getattr(obj, '_state', None) is None:
            obj._state = dict()
        if getattr(obj._state, 'fields_cache', None) is None:
            obj._state.fields_cache = dict()
        obj._state.fields_cache[field_name] = value


def del_fk_cache(obj: Model, field_name: str):
    'Delete a cached `ForeignKey` on the `Model`.'
    if not is_fk_cached(obj=obj, field_name=field_name):
        return
    if VERSION[0] == 1:
        delattr(obj, f'_{field_name}_cache')
    elif VERSION[0] == 2:
        del obj._state.fields_cache


_old_m2m_savedata = ManyToManyField.save_form_data


def _save_m2m_form_data(
        self: ManyToManyField, instance: Model, data: QuerySet):
    _old_m2m_savedata(self=self, instance=instance, data=data)
    set_prefetch_cache(
        relation=getattr(instance, self.name), queryset=data, override=True)


ManyToManyField.save_form_data = _save_m2m_form_data
