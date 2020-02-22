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
        keys = set(keys)
        my_keys = set(self)
        missing_keys = keys - my_keys
        if not missing_keys:
            return self
        self.update({x.pk: x for x in self.cache_updater(pk__in=missing_keys)})
        missing_keys = set(self) - keys
        if missing_keys:
            raise KeyError(f'The following keys are not found: {missing_keys}')
