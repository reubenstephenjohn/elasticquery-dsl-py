import copy
import typing as t
from typing_extensions import Self


class DSLQuery:
    """
    Base class for all Elasticsearch DSL query objects.

    Provides common functionality for constructing and combining queries.
    """

    __ror__: t.ClassVar[t.Callable[["DSLQuery", "DSLQuery"], "DSLQuery"]]
    __radd__: t.ClassVar[t.Callable[["DSLQuery", "DSLQuery"], "DSLQuery"]]
    __rand__: t.ClassVar[t.Callable[["DSLQuery", "DSLQuery"], "DSLQuery"]]

    def __init__(
        self, boost: t.Optional[float], _name: t.Optional[str]
    ) -> None:
        """
        Initialize a DSLQuery instance.

        Args:
            boost (Optional[float]): Boost value for the query.
            _name (Optional[str]): Optional name for the query.
        """
        self.boost = boost
        self.name = _name

    def _clone(self) -> Self:
        """
        Create a shallow copy of the query.

        Returns:
            DSLQuery: A new instance of the query with the same properties.
        """
        c = copy.copy(self)
        return c

    def _make_query(self) -> t.Dict[str, t.Any]:
        """
        Construct the query dict.

        This method should be implemented by subclasses.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    def to_query(self) -> t.Dict[str, t.Any]:
        """
        Get the Elasticsearch query dict.

        Returns:
            Dict[str, Any]: The query as a dict suitable for Elasticsearch.
        """
        return self._make_query()

    def __repr__(self) -> str:
        """
        Get the string representation of the query.

        Returns:
            str: A string representation of the query object.
        """
        return f"{self.__class__.__name__}({self._repr_params()})"

    def __eq__(self, other: t.Any) -> bool:
        """
        Check if this query is equal to another query.

        Args:
            other (Any): The other query to compare.

        Returns:
            bool: True if the queries are equal, False otherwise.
        """
        return (
            isinstance(other, self.__class__)
            and other.to_query() == self.to_query()
        )

    def __ne__(self, other: "DSLQuery") -> bool:
        """
        Check if this query is not equal to another query.

        Args:
            other (DSLQuery): The other query to compare.

        Returns:
            bool: True if the queries are not equal, False otherwise.
        """
        return not self == other

    def __or__(self, other: "DSLQuery"):
        """
        Overload the bitwise OR operator to create a boolean 'should' query.

        Args:
            q (DSLQuery): Another query to combine with this one.

        Returns:
            BoolQuery: A BoolQuery representing the logical 'should' of the two queries.
        """
        if hasattr(self, "__ror__"):
            return self.__ror__(other)
        if not isinstance(other, DSLQuery):
            raise NotImplementedError(
                f"Cannot perform `or` operation between a DSLQuery and {type(other).__name__} object"
            )
        return BoolQuery(should=BoolShould(self, other))

    def __and__(self, other: "DSLQuery"):
        """
        Overload the bitwise AND operator to create a boolean 'must' query.

        Args:
            q (DSLQuery): Another query to combine with this one.

        Returns:
            BoolQuery: A BoolQuery representing the logical 'must' of the two queries.
        """
        if hasattr(self, "__rand__"):
            return self.__rand__(other)
        if not isinstance(other, DSLQuery):
            raise NotImplementedError(
                f"Cannot perform `and` operation between a DSLQuery and {type(other).__name__} object"
            )
        return BoolQuery(must=BoolMust(self, other))

    def __add__(self, other: "DSLQuery"):
        """
        Overload the addition operator to create a boolean 'must' query.

        Args:
            q (DSLQuery): Another query to combine with this one.

        Returns:
            BoolQuery: A BoolQuery representing the logical 'must' of the two queries.
        """
        if hasattr(self, "__radd__"):
            return self.__radd__(other)
        if not isinstance(other, DSLQuery):
            raise NotImplementedError(
                f"Cannot perform `add` operation between a DSLQuery and {type(other).__name__} object"
            )
        return BoolQuery(must=BoolMust(self, other))

    def __invert__(self):
        """
        Overload the bitwise NOT operator to create a boolean 'must_not' query.

        Returns:
            BoolQuery: A BoolQuery representing the logical 'must_not' of this query.
        """
        return BoolQuery(must_not=BoolMustNot(self))

    def _repr_params(self) -> str:
        """
        Construct a string of the parameters for representation.

        Returns:
            str: A string representation of the query parameters.
        """
        return " | ".join(
            f"{n.replace('.', '__')}={v!r}"
            for n, v in self.__dict__.items()
            if v is not None and not isinstance(v, dict)
        )


# Logical DSL #


class LogicalDSL:
    """
    Base class for logical DSL queries like 'should', 'must', 'must_not', and 'filter'.

    This class handles multiple queries combined under a logical operator.
    """

    query_token = None

    def __init__(self, *args: DSLQuery):
        """
        Initialize a LogicalDSL instance.

        Args:
            *args (DSLQuery): The queries to combine under the logical operator.
        """
        self.queries = args

    def __add__(self, other: DSLQuery):
        if isinstance(other, self.__class__):
            return self.__class__(*self.queries, *other.queries)
        if isinstance(other, LogicalDSL):
            raise NotImplementedError(
                f"Cannot perform `add` operation between {self.__class__.__name__} and {other.__class__.__name__} objects"
            )
        if not isinstance(other, DSLQuery):
            raise NotImplementedError(
                f"Cannot perform `add` operation between a LogicalDSL and {type(other).__name__} object"
            )
        return self.__class__(*self.queries, other)

    __radd__ = __add__

    def __bool__(self):
        return bool(self.queries)

    def to_query(self) -> t.Dict[str, t.Any]:
        """ """
        return self._make_query()

    def _make_query(self) -> t.Dict[str, t.Any]:
        """
        Construct the query dict.

        Returns:
            Dict[str, Any]: The query as a dict with the logical operator and combined queries.
        """
        return {self.query_token: [q.to_query() for q in self.queries]}

    def _clone(self) -> Self:
        return self.__class__(*self.queries)


class BoolShould(LogicalDSL):
    """
    Represents a 'should' boolean query.

    Documents that match any of the queries in 'should' will match the BoolQuery.
    """

    query_token = "should"


class BoolMust(LogicalDSL):
    """
    Represents a 'must' boolean query.

    Documents must match all the queries in 'must' to match the BoolQuery.
    """

    query_token = "must"


class BoolMustNot(LogicalDSL):
    """
    Represents a 'must_not' boolean query.

    Documents must not match any of the queries in 'must_not' to match the BoolQuery.
    """

    query_token = "must_not"


class BoolFilter(LogicalDSL):
    """
    Represents a 'filter' boolean query.

    Filter context queries do not contribute to scoring.
    """

    query_token = "filter"


class BoolQuery(DSLQuery):
    """
    Represents a boolean query that can contain 'must', 'should', 'must_not', and 'filter' clauses.

    Allows combining multiple queries with boolean logic.
    """

    def __init__(
        self,
        should: t.Optional[BoolShould] = None,
        must: t.Optional[BoolMust] = None,
        must_not: t.Optional[BoolMustNot] = None,
        filter: t.Optional[BoolFilter] = None,
        boost: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initialize a BoolQuery instance.

        Args:
            should (Optional[BoolShould]): Optional 'should' queries.
            must (Optional[BoolMust]): Optional 'must' queries.
            must_not (Optional[BoolMustNot]): Optional 'must_not' queries.
            filter (Optional[BoolFilter]): Optional 'filter' queries.
            boost (Optional[float]): Optional boost value.
            _name (Optional[str]): Optional query name.
        """
        super().__init__(boost=boost, _name=_name)
        self.must = must or BoolMust()
        self.should = should or BoolShould()
        self.must_not = must_not or BoolMustNot()
        self.filter = filter or BoolFilter()

    def __add__(self, other: DSLQuery) -> "BoolQuery":
        """
        Combine this BoolQuery with another query using the 'must' clause.

        If the other query is also a BoolQuery, their clauses are merged.

        Args:
            other (DSLQuery): The other query to combine.

        Returns:
            BoolQuery: A new BoolQuery combining both queries under the 'must' clause.
        """
        q = self._clone()
        if isinstance(other, BoolQuery):
            q.must += other.must
            q.should += other.should
            q.must_not += other.must_not
            q.filter += other.filter
        else:
            if not isinstance(other, DSLQuery):
                raise NotImplementedError(
                    f"Cannot perform `add` operation between a DSLQuery and {type(other).__name__} object"
                )
            q.must += other
        return q

    __radd__ = __add__

    def __or__(self, other: DSLQuery) -> DSLQuery:
        """
        Combine this BoolQuery with another query using the 'should' clause.

        Args:
            other (DSLQuery): The other query to combine.

        Returns:
            BoolQuery: A new BoolQuery combining both queries under the 'should' clause.
        """
        for q in (self, other):
            if isinstance(q, BoolQuery) and not any(
                (
                    q.must,
                    q.must_not,
                    q.filter,
                    getattr(q, "minimum_should_match", None),
                )
            ):
                other = self if q is other else other
                q = q._clone()
                if isinstance(other, BoolQuery) and not any(
                    (
                        other.must,
                        other.must_not,
                        other.filter,
                        getattr(other, "minimum_should_match", None),
                    )
                ):
                    q.should += other.should
                else:
                    q.should += other
                return q
        if not isinstance(other, DSLQuery):
            raise NotImplementedError(
                f"Cannot perform `or` operation between a DSLQuery and {type(other).__name__} object"
            )
        return BoolQuery(should=[self, other])

    __ror__ = __or__

    def _make_query(self):
        """
        Construct the 'bool' query dict.

        Returns:
            Dict[str, Any]: The 'bool' query as a dict.
        """
        bool_query = {}
        if self.must:
            bool_query.update(self.must.to_query())
        if self.must_not:
            bool_query.update(self.must_not.to_query())
        if self.should:
            bool_query.update(self.should.to_query())
        if self.filter:
            bool_query.update(self.filter.to_query())
        if self.boost is not None:
            bool_query["boost"] = self.boost
        if self.name is not None:
            bool_query["_name"] = self.name
        if not bool_query:
            raise AttributeError("All boolean params cannot be None")
        return {"bool": bool_query}
