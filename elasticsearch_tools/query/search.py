import os
from typing import Optional

from .base import ElasticBaseQuery
from .bool import ElasticBoolMust, ElasticBoolShould


class ElasticSearchQuery(ElasticBaseQuery):
    def __and__(self, other: ElasticBaseQuery):
        return ElasticBoolMust(queries=[self, other])

    def __or__(self, other: ElasticBaseQuery):
        return ElasticBoolShould(queries=[self, other])


class ElasticQueryString(ElasticSearchQuery):
    field: Optional[str]
    value: Optional[str]
    query_type: str = "query_string"

    def __init__(self, field: Optional[str] = None, value: Optional[str] = None):
        self.field = field
        self.value = value

    def get_query(self) -> dict:
        return {"query_string": {"default_field": self.field or "*", "query": self.value or "*"}}


class ElasticTermQuery(ElasticSearchQuery):
    field: str
    value: str
    query_type: str = "term"

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    def get_query(self) -> dict:
        return {self.query_type: {self.field: self.value.strip('"')}}


class ElasticFuzzyQuery(ElasticTermQuery):
    query_type: str = "fuzzy"


class ElasticExistsQuery(ElasticSearchQuery):
    field: str
    query_type: str = "exists"

    def __init__(self, field: str):
        self.field = field

    def get_query(self) -> dict:
        return {"exists": {"field": self.field}}


class ElasticFullMatchQuery(ElasticSearchQuery):
    field: str
    value: str
    boosting: Optional[int]
    query_type: str = "match_phrase"

    def __init__(self, field: str, value: str, boosting: Optional[int] = None):
        self.field = field
        self.value = value
        self.boosting = boosting

    def get_query(self) -> dict:
        subquery = {self.field: self.value.strip('"')}
        if self.boosting:
            subquery["boosting"] = self.boosting
        return {self.query_type: subquery}


class ElasticMatchQuery(ElasticFullMatchQuery):
    query_type: str = "match"


class ElasticRangeQuery(ElasticSearchQuery):
    field: str
    value_from: int
    value_to: int
    query_type: str = "range"

    def __init__(self, field: str, value_from: int, value_to: int):
        self.field = field
        self.value_from = min(value_from, value_to)
        self.value_to = max(value_from, value_to)

    def get_query(self) -> dict:
        return {"range": {self.field: {"gte": self.value_from, "lte": self.value_to}}}


class ElasticGeoPointRangeQuery(ElasticSearchQuery):
    field: str
    value_from: str
    value_to: str
    query_type: str = "geo_point_range"

    def __init__(self, field: str, value_from: str, value_to: str):
        self.field = field
        self.value_from = value_from
        self.value_to = value_to

    @staticmethod
    def get_coordinates(value):
        value = value.strip('"')
        value = value.lstrip("[").rstrip("]")
        coords = value.split(",")
        return {"lat": coords[0], "lon": coords[1]}

    def get_query(self):
        return {
            "geo_bounding_box": {
                "location.coordinates": {
                    "top_left": self.get_coordinates(self.value_from),
                    "bottom_right": self.get_coordinates(self.value_to),
                }
            }
        }


class ElasticGeoPointQuery(ElasticSearchQuery):
    field: str
    value: str
    query_type: str = "geo_point"

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    def get_query(self):
        return ElasticGeoPointRangeQuery(field=self.field, value_from=self.value, value_to=self.value).get_query()


class ElasticNestedQuery(ElasticSearchQuery):
    query: ElasticBaseQuery
    nested_path: Optional[str]
    query_type: str = "nested"

    def __init__(self, query: ElasticBaseQuery, nested_path: Optional[str] = None):
        self.query = query
        self.nested_path = nested_path

    def _path(self):
        if self.nested_path:
            return self.nested_path
        else:
            return os.getenv("DEFAULT_NESTED_PATH")

    def get_query(self) -> dict:
        return {"nested": {"path": self._path(), "query": self.query.get_query()}}

