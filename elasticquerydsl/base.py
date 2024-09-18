import copy
import typing as t
from typing_extensions import Self


class DSLQuery:
    __ror__: t.ClassVar[t.Callable[["DSLQuery", "DSLQuery"], "DSLQuery"]]
    __radd__: t.ClassVar[t.Callable[["DSLQuery", "DSLQuery"], "DSLQuery"]]
    __rand__: t.ClassVar[t.Callable[["DSLQuery", "DSLQuery"], "DSLQuery"]]

    def __init__(
        self, boost: t.Optional[float], _name: t.Optional[str]
    ) -> None:
        self.boost = boost
        self.name = _name

    def _clone(self) -> Self:
        c = copy.copy(self)
        return c

    def _make_query(self) -> t.Dict[str, t.Any]:
        raise NotImplementedError

    def to_query(self) -> t.Dict[str, t.Any]:
        return self._make_query()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._repr_params()})"

    def __eq__(self, other: t.Any) -> bool:
        return (
            isinstance(other, self.__class__)
            and other.to_dict() == self.to_dict()
        )

    def __ne__(self, other: "DSLQuery") -> bool:
        return not self == other

    def __or__(self, q: "DSLQuery"):
        if hasattr(self, "__ror__"):
            return self.__ror__(q)
        return BoolQuery(should=BoolShould(self, q))

    def __and__(self, q: "DSLQuery"):
        if hasattr(self, "__rand__"):
            return self.__rand__(q)
        return BoolQuery(must=BoolMust(self, q))

    def __add__(self, q: "DSLQuery"):
        if hasattr(self, "__radd__"):
            return self.__radd__(q)
        return BoolQuery(must=BoolMust(self, q))

    def __invert__(self):
        return BoolQuery(must_not=BoolMustNot(self))

    def _repr_params(self) -> str:
        """Produce a repr of all our parameters to be used in __repr__."""
        # TODO | Update this
        return "|".join(
            f"{n.replace('.', '__')}={v!r}"
            for (n, v) in sorted(self.__dict__.items())
        )


# Logical DSL #


class LogicalDSL(DSLQuery):
    query_token = None

    def __init__(self, *args: DSLQuery):
        self.queries = args
        super().__init__(boost=None, _name=None)

    def _make_query(self):
        return {self.query_token: [q.to_query() for q in self.queries]}


class BoolShould(LogicalDSL):
    query_token = "should"


class BoolMust(LogicalDSL):
    query_token = "must"


class BoolMustNot(LogicalDSL):
    query_token = "must_not"


class BoolFilter(LogicalDSL):
    query_token = "filter"


class BoolQuery(DSLQuery):
    def __init__(
        self,
        should: t.Optional[BoolShould] = None,
        must: t.Optional[BoolMust] = None,
        must_not: t.Optional[BoolShould] = None,
        filter: t.Optional[BoolFilter] = None,
        boost: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        super().__init__(boost=boost, _name=_name)
        self.must = must
        self.should = should
        self.must_not = must_not
        self.filter = filter
        self.bool_query = self._make_query()

    def __add__(self, other: DSLQuery) -> "BoolQuery":
        q = self._clone()
        if isinstance(other, BoolQuery):
            q.must += other.must
            q.should += other.should
            q.must_not += other.must_not
            q.filter += other.filter
        else:
            q.must.append(other)
        return q

    __radd__ = __add__

    def __or__(self, other: DSLQuery) -> DSLQuery:
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
                    q.should.extend(other.should)
                else:
                    q.should.append(other)
                return q

        return BoolQuery(should=[self, other])

    __ror__ = __or__

    def to_query(self):
        return self.bool_query

    def _make_query(self):
        bool_query = {}
        if self.must is not None:
            bool_query.update(self.must.to_query())
        if self.must_not is not None:
            bool_query.update(self.must_not.to_query())
        if self.should is not None:
            bool_query.update(self.should.to_query())
        if self.filter is not None:
            bool_query.update(self.filter.to_query())
        if self.boost is not None:
            bool_query["boost"] = self.boost
        if self.name is not None:
            bool_query["_name"] = self.name
        if not bool_query:
            raise AttributeError("All boolean params cannot be None")
        return {"bool": bool_query}
