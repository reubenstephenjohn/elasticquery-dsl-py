from elasticquerydsl.base import DSLQuery
from elasticquerydsl.logical import (
    BoolQuery,
    BoolFilter,
    BoolMust,
    BoolMustNot,
    BoolShould,
)


class BooleanDSLBuilder:
    def __init__(self):
        self.should = []
        self.must = []
        self.must_not = []
        self.filter = []
        self.boost = None
        self.name = None

    def set_name(self, name: str):
        self.name = name

    def set_boost(self, boost: float):
        self.boost = boost

    def add_should_query(self, *query: DSLQuery):
        self.should.extend(query)

    def add_must_query(self, *query: DSLQuery):
        self.must.extend(query)

    def add_must_not_query(self, *query: DSLQuery):
        self.must_not.extend(query)

    def add_filter_query(self, *query: DSLQuery):
        self.filter.extend(query)

    def build(self) -> BoolQuery:
        query = BoolQuery(
            should=BoolShould(*self.should) if self.should else None,
            must=BoolMust(*self.must) if self.must else None,
            must_not=BoolMustNot(*self.must_not) if self.must_not else None,
            filter=BoolFilter(*self.filter) if self.filter else None,
            boost=self.boost,
            _name=self.name,
        )
        return query
