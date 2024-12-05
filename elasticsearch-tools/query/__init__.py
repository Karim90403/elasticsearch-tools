from typing import Optional

from .base import ElasticBaseQuery
from .bool import ElasticBoolMust, ElasticBoolMustNot, ElasticBoolShould, ElasticBoolQuery
from .search import ElasticQueryString, ElasticTermQuery, ElasticNestedQuery, ElasticExistsQuery, ElasticRangeQuery, ElasticGeoPointQuery, ElasticGeoPointRangeQuery, ElasticFullMatchQuery

bool_queries = dict()

for bool_query in ElasticBoolQuery.__subclasses__():
    bool_queries[bool_query.query_type] = bool_query

search_queries = dict()

for search_query in ElasticBaseQuery.__subclasses__():
    search_queries[search_query.query_type] = search_query


def generate_query(_type: Optional[str], *args, **kwargs):
    if _type:
        query_class = bool_queries.get(_type) or search_queries.get(_type) or ElasticBaseQuery
        return query_class(*args, **kwargs)
    return dict(**kwargs)
