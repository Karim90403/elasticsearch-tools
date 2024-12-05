import os
from typing import Optional

from query.base import ElasticBaseQuery


class ElasticQueryString(ElasticBaseQuery):
    field: Optional[str]
    value: Optional[str]

    def __init__(self, field: Optional[str], value: Optional[str]):
        self.field = field
        self.value = value

    def get_query(self) -> dict:
        return {"query_string": {"default_field": self.field or "*", "query": self.value or "*"}}


class ElasticTermQuery(ElasticBaseQuery):
    field: str
    value: str

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    def get_query(self) -> dict:
        return {"term": {self.field: self.value.strip('"')}}


class ElasticExistsQuery(ElasticBaseQuery):
    field: str

    def __init__(self, field: str):
        self.field = field

    def get_query(self) -> dict:
        return {"exists": {"field": self.field}}


class ElasticFullMatchQuery(ElasticBaseQuery):
    field: str
    value: str

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    def get_query(self) -> dict:
        return {"match_phrase": {self.field: self.value.strip('"')}}


class ElasticRangeQuery(ElasticBaseQuery):
    field: str
    value_from: int
    value_to: int

    def __init__(self, field: str, value_from: int, value_to: int):
        self.field = field
        self.value_from = value_from
        self.value_to = value_to

    def get_query(self) -> dict:
        return {"range": {self.field: {"gte": self.value_from, "lte": self.value_to}}}


class ElasticGeoPointRangeQuery(ElasticBaseQuery):
    field: str
    value_from: str
    value_to: str

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


class ElasticGeoPointQuery(ElasticBaseQuery):
    field: str
    value: str

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    def get_query(self):
        return ElasticGeoPointRangeQuery(field=self.field, value_from=self.value, value_to=self.value).get_query()


class ElasticNestedQuery(ElasticBaseQuery):
    query: ElasticBaseQuery
    nested_path: Optional[str]

    def _path(self):
        if self.nested_path:
            return self.nested_path
        else:
            return os.getenv("DEFAULT_NESTED_PATH")

    def get_query(self) -> dict:
        return {"nested": {"path": self._path(), "query": self.query}}

