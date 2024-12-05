from __future__ import annotations


class ElasticBaseQuery(object):
    def get_query(self) -> dict:
        return {}

    def __and__(self, other: ElasticBaseQuery):
        pass

    def __or__(self, other: ElasticBaseQuery):
        pass

    def __rand__(self, other):
        self.__and__(other)

    def __ror__(self, other):
        self.__or__(other)
