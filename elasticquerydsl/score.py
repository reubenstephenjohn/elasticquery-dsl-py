import typing as t
from .base import DSLQuery


class ConstantScoreQuery(DSLQuery):
    def __init__(
        self,
        filter_query: DSLQuery,
        boost: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a ConstantScoreQuery object.

        Use Cases:
        - Assigns a constant score to matching documents, ignoring the relevance score from the query.

        Args:
            filter_query (dict): The query to filter documents.
            boost (float, optional): Boost value to influence the constant score of matching documents. [default: 1.0]
            _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost, _name)
        self.filter_query = filter_query
        self.constant_score_query = self._make_query()

    def to_query(self):
        return self.constant_score_query

    def _make_query(self):
        const_score_subquery = {"filter": self.filter_query.to_query()}

        if self.boost is not None:
            const_score_subquery["boost"] = self.boost
        if self.name:
            const_score_subquery["_name"] = self.name

        return {"constant_score": const_score_subquery}


class FunctionScoreQuery(DSLQuery):
    def __init__(
        self,
        query: t.Dict[str, t.Any],
        functions: t.List[t.Dict[str, t.Any]] = None,
        score_mode: t.Optional[str] = None,
        boost_mode: t.Optional[str] = None,
        max_boost: t.Optional[float] = None,
        min_score: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a FunctionScoreQuery object.

        Use Cases:
        - Modify document scores based on the result of a query and a set of functions.

        Args:
            query (dict): The base query to modify scores.
            functions (list, optional): List of functions to apply to modify document scores. [default: None]
            score_mode (str, optional): How to combine the results of functions. [default: 'multiply']
            boost_mode (str, optional): How to combine the base query score with function scores. [default: 'multiply']
            max_boost (float, optional): Maximum boost that can be applied. [default: None]
            min_score (float, optional): Minimum score required for the document to be included in the result. [default: None]
            _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost=None, _name=_name)
        self.query = query
        self.functions = functions
        self.score_mode = score_mode
        self.boost_mode = boost_mode
        self.max_boost = max_boost
        self.min_score = min_score
        self.function_score_query = self._make_query()

    def to_query(self):
        return self.function_score_query

    def _make_query(self):
        func_score_subquery = {"query": self.query}

        if self.functions:
            func_score_subquery["functions"] = self.functions
        if self.score_mode:
            func_score_subquery["score_mode"] = self.score_mode
        if self.boost_mode:
            func_score_subquery["boost_mode"] = self.boost_mode
        if self.max_boost is not None:
            func_score_subquery["max_boost"] = self.max_boost
        if self.min_score is not None:
            func_score_subquery["min_score"] = self.min_score
        if self.name:
            func_score_subquery["_name"] = self.name

        return {"function_score": func_score_subquery}
