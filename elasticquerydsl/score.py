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
            filter_query (DSLQuery): The query to filter documents.
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
        query: t.Optional[DSLQuery] = None,
        functions: t.Optional[t.List["ScoreFunction"]] = None,
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
            query (DSLQuery | None): The base query to modify scores.
            functions (list[ScoreFunction], optional): List of functions to apply to modify document scores. [default: None]
            score_mode (str, optional): How to combine the results of functions. [default: 'multiply']
            boost_mode (str, optional): How to combine the base query score with function scores. [default: 'multiply']
            max_boost (float, optional): Maximum boost that can be applied. [default: None]
            min_score (float, optional): Minimum score required for the document to be included in the result. [default: None]
            _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost=None, _name=_name)
        self.query = query
        self.functions = functions or []
        self.score_mode = score_mode
        self.boost_mode = boost_mode
        self.max_boost = max_boost
        self.min_score = min_score
        self.function_score_query = self._make_query()

    def to_query(self):
        return self.function_score_query

    def _make_query(self):
        func_score_subquery = {}

        if self.query:
            func_score_subquery["query"] = self.query.to_query()

        functions = [f.to_query() for f in self.functions]
        if functions:
            func_score_subquery["functions"] = functions
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


class ScoreFunction:
    """
    Base class for score functions in Elasticsearch queries.

    All score function subclasses must implement the to_query() method to generate
    their Elasticsearch query representation.
    """

    def __init__(
        self,
        query: t.Optional[DSLQuery] = None,
        weight: t.Optional[float] = None,
    ):
        """
        Initialize base ScoreFunction.

        Args:
            query (DSLQuery, optional): Query to filter which documents this function applies to
            weight (float, optional): Weight to apply to this function's score
        """
        self.query = query
        self.weight = weight

    def to_query(self):
        raise NotImplementedError(
            f"`to_query` func not implemented in subclass: {type(self).__name__}"
        )


class ScriptScoreFunction(ScoreFunction):
    def __init__(
        self,
        script: str,
        query: t.Optional[DSLQuery] = None,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        lang: t.Optional[str] = None,
        weight: t.Optional[float] = None,
    ):
        """
        Initializes a ScriptScoreFunction object.

        Use Cases:
        - Custom scoring based on script logic
        - Complex score calculations using document fields and parameters
        - Dynamic scoring based on runtime calculations

        Args:
            script (str): The script to calculate the score
            query (DSLQuery, optional): Query to filter which documents this function applies to
            params (dict, optional): Parameters to pass to the script
            lang (str, optional): Script language (defaults to 'painless')
            weight (float, optional): Weight to apply to this function's score
        """
        super().__init__(query=query, weight=weight)
        self.script = script
        self.params = params
        self.lang = lang

    def to_query(self):
        script_score = {"script_score": {"script": {"source": self.script}}}

        if self.params:
            script_score["script_score"]["script"]["params"] = self.params
        if self.lang:
            script_score["script_score"]["script"]["lang"] = self.lang
        if self.query:
            script_score["filter"] = self.query.to_query()
        if self.weight is not None:
            script_score["weight"] = self.weight

        return script_score


class RandomScoreFunction(ScoreFunction):
    def __init__(
        self,
        seed: t.Optional[int] = None,
        field: t.Optional[str] = None,
        query: t.Optional[DSLQuery] = None,
        weight: t.Optional[float] = None,
    ):
        """
        Initializes a RandomScoreFunction object.

        Use Cases:
        - Randomize document ordering in search results
        - A/B testing different document rankings
        - Adding controlled randomness to search results

        Args:
            seed (int, optional): Seed value for random number generation
            field (str, optional): Field to use for random number generation
            query (DSLQuery, optional): Query to filter which documents this function applies to
            weight (float, optional): Weight to apply to this function's score
        """
        super().__init__(query=query, weight=weight)
        self.seed = seed
        self.field = field

    def to_query(self):
        random_score = {"random_score": {}}

        if self.seed is not None:
            random_score["random_score"]["seed"] = self.seed
        if self.field:
            random_score["random_score"]["field"] = self.field
        if self.query:
            random_score["filter"] = self.query.to_query()
        if self.weight is not None:
            random_score["weight"] = self.weight

        return random_score


class FieldValueFactorFunction(ScoreFunction):
    def __init__(
        self,
        field: str,
        factor: t.Optional[float] = None,
        modifier: t.Optional[str] = None,
        missing: t.Optional[float] = None,
        query: t.Optional[DSLQuery] = None,
        weight: t.Optional[float] = None,
    ):
        """
        Initializes a FieldValueFactorFunction object.

        Use Cases:
        - Boost documents based on numeric field values
        - Influence scoring based on popularity metrics
        - Adjust relevance based on document attributes

        Args:
            field (str): Field to use for scoring
            factor (float, optional): Factor to multiply field value with
            modifier (str, optional): Modifier to apply to field value
                                    (none|log|log1p|log2p|ln|ln1p|ln2p|square|sqrt|reciprocal)
            missing (float, optional): Value to use if document doesn't have the field
            query (DSLQuery, optional): Query to filter which documents this function applies to
            weight (float, optional): Weight to apply to this function's score
        """
        super().__init__(query=query, weight=weight)
        self.field = field
        self.factor = factor
        self.modifier = modifier
        self.missing = missing

    def to_query(self):
        field_value_factor = {"field_value_factor": {"field": self.field}}

        if self.factor is not None:
            field_value_factor["field_value_factor"]["factor"] = self.factor
        if self.modifier:
            field_value_factor["field_value_factor"][
                "modifier"
            ] = self.modifier
        if self.missing is not None:
            field_value_factor["field_value_factor"]["missing"] = self.missing
        if self.query:
            field_value_factor["filter"] = self.query.to_query()
        if self.weight is not None:
            field_value_factor["weight"] = self.weight

        return field_value_factor


class DecayFunction(ScoreFunction):
    def __init__(
        self,
        decay_type: str,
        field: str,
        origin: t.Any,
        scale: t.Any,
        offset: t.Optional[t.Any] = None,
        decay: t.Optional[float] = None,
        query: t.Optional[DSLQuery] = None,
        multi_value_mode: t.Optional[str] = None,
        weight: t.Optional[float] = None,
    ):
        """
        Initializes a DecayFunction object.

        Use Cases:
        - Distance-based scoring for geographical searches
        - Time-based decay for recent/older documents
        - Numeric field proximity scoring

        Args:
            decay_type (str): Type of decay function ('gauss', 'exp', or 'linear')
            field (str): Field to calculate decay on
            origin (Any): Central point from which the decay function is computed
            scale (Any): Required distance from origin at which score is decay
            offset (Any, optional): Distance from origin where decay begins
            decay (float, optional): Score at scale distance from origin
            query (DSLQuery, optional): Query to filter which documents this function applies to
            multi_value_mode (str, optional): How to handle multi-valued fields
                                            (min|max|avg|sum)
            weight (float, optional): Weight to apply to this function's score
        """
        super().__init__(query=query, weight=weight)
        self.decay_type = decay_type
        self.field = field
        self.origin = origin
        self.scale = scale
        self.offset = offset
        self.decay = decay
        self.multi_value_mode = multi_value_mode

    def to_query(self):
        decay_function = {
            self.decay_type: {
                self.field: {"origin": self.origin, "scale": self.scale}
            }
        }

        if self.offset is not None:
            decay_function[self.decay_type][self.field]["offset"] = self.offset
        if self.decay is not None:
            decay_function[self.decay_type][self.field]["decay"] = self.decay
        if self.multi_value_mode:
            decay_function[self.decay_type][self.field][
                "multi_value_mode"
            ] = self.multi_value_mode
        if self.query:
            decay_function["filter"] = self.query.to_query()
        if self.weight is not None:
            decay_function["weight"] = self.weight

        return decay_function


class WeightFunction(ScoreFunction):
    def __init__(
        self,
        weight: float,
        query: t.Optional[DSLQuery] = None,
    ):
        """
        Initializes a WeightFunction object.

        Use Cases:
        - Apply constant boost to matching documents
        - Prioritize specific document sets
        - Simple score adjustments based on filters

        Args:
            weight (float): Weight to apply to matching documents
            query (DSLQuery, optional): Query to filter which documents this function applies to
        """
        super().__init__(query=query, weight=weight)

    def to_query(self):
        weight_function = {"weight": self.weight}

        if self.query:
            weight_function["filter"] = self.query.to_query()

        return weight_function
