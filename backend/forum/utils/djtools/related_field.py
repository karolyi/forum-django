from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Tuple

from django import VERSION
from django.db.models.base import Model
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models.fields.reverse_related import ManyToManyRel, ManyToOneRel

from .query_cache import get_prefetch_cache_key


@dataclass(frozen=True)
class RemoteForeignKeyResult(object):
    """
    Result of a `ForeignKey` reverse relations lookup.
    The name used for annotation/aggregation expressions is
    `prefetch_cache_key`.
    """
    # The model on the other side
    model: Model
    # The field on the original model
    field: ForeignKey
    # The cache key
    prefetch_cache_key: str
    # Name used for annotation
    annotation_key: str


@dataclass(frozen=True)
class RemoteManyToManyResult(object):
    """
    Result of a `ManyToMany` reverse relations lookup.
    The name used for annotation/aggregation expressions is
    `prefetch_cache_key`.
    """
    # The field on the model
    m2m_field: ManyToManyField
    # The cache key
    prefetch_cache_key: str
    # The intermediate model
    through: Model
    # The model's key in the intermediate
    through_fk_mine: ForeignKey
    # Other model's key in the intermediate
    through_fk_other: ForeignKey


@lru_cache(maxsize=None)
def get_reverse_fk_relations(
        model: Model) -> Dict[str, RemoteForeignKeyResult]:
    """
    Return a `dict` of `str-RemoteForeignKeyResult` relations.
    That is, one-to-many relations where the passed model has
    `ForeignKey`s pointing to it from remote models.
    """
    result = dict()
    related_fields = [
        x for x in model._meta.get_fields()
        if x.is_relation and x.auto_created and not x.concrete]
    fk_fields = [x for x in related_fields if x.one_to_many or x.one_to_one]
    for rel_field in fk_fields:  # type: ManyToOneRel
        related_name = rel_field.related_name or f'{rel_field.name}_set'
        prefetch_cache_key = get_prefetch_cache_key(
            relation=getattr(model, related_name))
        result.update({related_name: RemoteForeignKeyResult(
            model=rel_field.related_model, field=rel_field.field,
            prefetch_cache_key=prefetch_cache_key,
            annotation_key=rel_field.related_name or rel_field.name)})
    return result


@lru_cache(maxsize=None)
def get_reverse_m2m_relations(
        model: Model) -> Dict[str, RemoteManyToManyResult]:
    """
    Return a `dict` of `str-RemoteManyToManyResult` relations.
    That is, many-to-many relations where the passed model has
    `ManyToManyField`s pointing to it from remote models.
    """
    result = dict()
    m2m_fields = [
        x for x in model._meta.get_fields()
        if x.is_relation and x.many_to_many]
    for field in m2m_fields:
        rel_field, m2m_field = (field, field.remote_field) \
            if type(field) is ManyToManyRel else \
            (field.remote_field, field)  # type: ManyToManyRel, ManyToManyField
        related_name = m2m_field.name
        prefetch_cache_key = m2m_field.name
        if type(field) is ManyToManyRel:
            related_name = rel_field.related_name or f'{rel_field.name}_set'
            prefetch_cache_key = rel_field.related_name or rel_field.name
        fk_mine, fk_other = get_m2mthrough_fk_fields(
            from_model=model, m2m_field=m2m_field)
        result.update({related_name: RemoteManyToManyResult(
            m2m_field=m2m_field, prefetch_cache_key=prefetch_cache_key,
            through=rel_field.through,
            through_fk_mine=fk_mine, through_fk_other=fk_other)})
    return result


def get_m2mthrough_fk_fields(
    m2m_field: ManyToManyField, from_model: Model
) -> Tuple[ForeignKey, ForeignKey]:
    """
    Return the two `ForeignKey` sides from a through model of a
    many-to-many relationship.
    """
    from_name, to_name = \
        (m2m_field.m2m_field_name(), m2m_field.m2m_reverse_field_name()) \
        if from_model == m2m_field.model else \
        (m2m_field.m2m_reverse_field_name(), m2m_field.m2m_field_name())
    if VERSION[0] == 1:
        m2m_model = m2m_field.rel.through
    elif VERSION[0] == 2:
        m2m_model = m2m_field.remote_field.through
    fk_from = m2m_model._meta.get_field(from_name)
    fk_to = m2m_model._meta.get_field(to_name)
    return fk_from, fk_to
