from __future__ import annotations

from typing import List

from query.base import ElasticBaseQuery


class ElasticBoolQuery(ElasticBaseQuery):
    queries: List[ElasticBaseQuery]
    query_type = "bool_base"

    def __init__(self, queries: List[ElasticBaseQuery]):
        self.queries = queries or []

    def __and__(self, other: ElasticBaseQuery):
        if isinstance(other, ElasticBoolMust):
            return ElasticBoolMust(queries=self.queries + other.queries)
        elif isinstance(self, ElasticBoolMust):
            return ElasticBoolMust(queries=self.queries + [other])
        return ElasticBoolMust(queries=[self, other])

    def __or__(self, other: ElasticBaseQuery):
        if isinstance(other, ElasticBoolShould):
            return ElasticBoolShould(queries=self.queries + other.queries)
        elif isinstance(self, ElasticBoolShould):
            return ElasticBoolShould(queries=self.queries + [other])
        return ElasticBoolShould(queries=[self, other])

    def get_query(self):
        return {"bool": {self.query_type: [q.get_query() for q in self.queries]}}


class ElasticBoolMustNot(ElasticBoolQuery):
    query_type = "must_not"

    def __invert__(self):
        return ElasticBoolMust(queries=self.queries)


class ElasticBoolShould(ElasticBoolQuery):
    query_type = "should"

    def __invert__(self):
        return ElasticBoolMustNot(queries=[self])


class ElasticBoolMust(ElasticBoolQuery):
    query_type = "must"

    def __invert__(self):
        return ElasticBoolMustNot(queries=self.queries)
