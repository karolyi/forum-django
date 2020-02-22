from __future__ import annotations

from collections import UserDict
from random import random
from typing import Any, Iterable


class ModelCacheBase(UserDict):
    'Model cache base.'
    _request = None
    model = None
    cache_getter = None
    cache_updater = None

    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('request') if 'request' in kwargs \
            else random()
        if not self.cache_getter:
            raise NotImplementedError('No cache_getter set!')
        if not self.cache_updater:
            raise NotImplementedError('No cache_updater set!')
        self._errored_keys = set()
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: int):
        if key in self.data:
            return self.data[key]
        try:
            self.data[key] = self.cache_getter(pk=key)
            return self.data[key]
        except self.model.DoesNotExist:
            raise KeyError(key)

    def get(self, key: int, default: Any = None):
        'Failsafe value getting.'
        try:
            return self[key]
        except KeyError:
            return default

    def fetch_keys(self, keys: Iterable[int]):
        'Update with the passed `keys`, fetch them if necessary.'
        keys = keys if type(keys) is set else set(keys)
        self_keys = set(self)
        already_errored_keys = self._errored_keys.intersection(keys)
        missing_keys = keys - self_keys - already_errored_keys
        if not missing_keys:
            if already_errored_keys:
                raise KeyError(already_errored_keys)
            return
        self.update({x.pk: x for x in self.cache_updater(pk__in=missing_keys)})
        missing_keys = keys - set(self)
        if missing_keys:
            self._errored_keys.update(missing_keys - already_errored_keys)
            raise KeyError(missing_keys)
