from elasticquerydsl.base import DSLQuery
from elasticquerydsl.base import (
    BoolQuery,
    BoolFilter,
    BoolMust,
    BoolMustNot,
    BoolShould,
)


class BooleanDSLBuilder:
    """
    Builder class for constructing complex Boolean DSL queries in Elasticsearch.

    This class allows you to incrementally build a `BoolQuery` by adding various clauses such as
    'must', 'should', 'must_not', and 'filter'. It provides a fluent interface to help construct
    queries in a readable and manageable way.
    """

    def __init__(self):
        """Initialize a new instance of `BooleanDSLBuilder`."""
        self.should = []
        self.must = []
        self.must_not = []
        self.filter = []
        self.boost = None
        self.name = None

    def set_name(self, name: str):
        """
        Set the name for the Boolean query.

        Args:
            name (str): The name to assign to the query.
        """
        self.name = name
        return self

    def set_boost(self, boost: float):
        """
        Set the boost value for the Boolean query.

        Args:
            boost (float): The boost factor to apply to the query.
        """
        self.boost = boost
        return self

    def add_should_query(self, *query: DSLQuery):
        """
        Add one or more queries to the 'should' clause.

        Args:
            *query (DSLQuery): One or more `DSLQuery` instances to add to the 'should' clause.
        """
        self.should.extend(query)
        return self

    def add_must_query(self, *query: DSLQuery):
        """
        Add one or more queries to the 'must' clause.

        Args:
            *query (DSLQuery): One or more `DSLQuery` instances to add to the 'must' clause.
        """
        self.must.extend(query)
        return self

    def add_must_not_query(self, *query: DSLQuery):
        """
        Add one or more queries to the 'must_not' clause.

        Args:
            *query (DSLQuery): One or more `DSLQuery` instances to add to the 'must_not' clause.
        """
        self.must_not.extend(query)
        return self

    def add_filter_query(self, *query: DSLQuery):
        """
        Add one or more queries to the 'filter' clause.

        Args:
            *query (DSLQuery): One or more `DSLQuery` instances to add to the 'filter' clause.
        """
        self.filter.extend(query)
        return self

    def build(self) -> BoolQuery:
        """
        Build and return the `BoolQuery` object with the accumulated clauses.

        Returns:
            BoolQuery: The constructed `BoolQuery` combining all the added clauses.
        """
        if not any((self.should, self.must, self.must_not, self.filter)):
            raise AttributeError("All boolean params cannot be None")

        query = BoolQuery(
            should=BoolShould(*self.should) if self.should else None,
            must=BoolMust(*self.must) if self.must else None,
            must_not=BoolMustNot(*self.must_not) if self.must_not else None,
            filter=BoolFilter(*self.filter) if self.filter else None,
            boost=self.boost,
            _name=self.name,
        )
        return query
