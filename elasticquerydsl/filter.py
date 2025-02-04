import typing as t
from elasticquerydsl.base import DSLQuery


class FilterDSL(DSLQuery):
    """
    Base class for filter queries in Elasticsearch DSL.

    This class serves as the foundation for queries that are primarily used in
    filter context and do not contribute to scoring.
    """

    def __init__(
        self, boost: t.Optional[float] = None, _name: t.Optional[str] = None
    ):
        """
        Initialize a FilterDSL instance.

        Args:
            boost (Optional[float]): Boost value to influence the relevance score of matching documents.
            _name (Optional[str]): Optional name for the query.
        """
        self.boost = boost
        self.name = _name

    def _make_query(self):
        """
        Construct the query dictionary.

        This method should be implemented by subclasses.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError


class MatchAllQuery(FilterDSL):
    def __init__(
        self,
        boost: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a MatchAllQuery object.

        Use Cases:
        - Retrieve all documents in the index, optionally applying a boost to the relevance score of the documents.

        Args:
            boost (float, optional): Boost value to influence the relevance score of matching documents. [default: 1.0]
            _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost, _name)
        self.match_all_query = self._make_query()

    def __add__(self, other: DSLQuery) -> DSLQuery:
        if not isinstance(other, DSLQuery):
            raise NotImplementedError(
                f"Cannot perform `add` operation between a DSLQuery and {type(other).__name__} object"
            )
        return other._clone()

    __and__ = __rand__ = __radd__ = __add__

    def __or__(self, other: DSLQuery) -> DSLQuery:
        return self

    __ror__ = __or__

    def __invert__(self) -> "MatchNoneQuery":
        return MatchNoneQuery()

    def to_query(self):
        return self.match_all_query

    def _make_query(self):
        match_all_subquery = {}

        if self.boost is not None:
            match_all_subquery["boost"] = self.boost
        if self.name:
            match_all_subquery["_name"] = self.name

        return {"match_all": match_all_subquery}


class MatchNoneQuery(FilterDSL):
    def __init__(
        self,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a MatchNoneQuery object.

        Use Cases:
        - Match no documents at all. This query can be used in scenarios where you want an empty result set or need to negate other queries.

        Args:
            _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost=None, _name=_name)
        self.match_none_query = self._make_query()

    def __add__(self, other: DSLQuery) -> "MatchNoneQuery":
        return self

    __and__ = __rand__ = __radd__ = __add__

    def __or__(self, other: DSLQuery) -> DSLQuery:
        if not isinstance(other, DSLQuery):
            raise NotImplementedError(
                f"Cannot perform `or` operation between a DSLQuery and {type(other).__name__} object"
            )
        return other._clone()

    __ror__ = __or__

    def __invert__(self) -> MatchAllQuery:
        return MatchAllQuery()

    def to_query(self):
        return self.match_none_query

    def _make_query(self):
        match_none_subquery = {}

        if self.name:
            match_none_subquery["_name"] = self.name

        return {"match_none": match_none_subquery}


class MatchQuery(FilterDSL):
    def __init__(
        self,
        field: str,
        value: t.Any,
        operator: t.Optional[str] = None,
        zero_terms_query: t.Optional[str] = None,
        fuzziness: t.Optional[t.Union[str, int]] = None,
        prefix_length: t.Optional[int] = None,
        max_expansions: t.Optional[int] = None,
        minimum_should_match: t.Optional[t.Union[str, int]] = None,
        analyzer: t.Optional[str] = None,
        auto_generate_synonyms_phrase_query: t.Optional[bool] = None,
        boost: t.Optional[float] = None,
        lenient: t.Optional[bool] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a MatchQuery object.

        :param field: The field to match against.
        :param query: The query string to match.
        :param operator: Optional, operator to use for the query ('and' or 'or'). [default: 'or']
        :param zero_terms_query: Optional, what to do when the query results in zero terms ('none' or 'all'). [default: 'none']
        :param fuzziness: Optional, defines the fuzziness (e.g., 'AUTO', 1, 2). [default: None]
        :param prefix_length: Optional, length of the prefix to apply fuzziness. [default: 0]
        :param max_expansions: Optional, maximum number of terms to expand the query to. [default: 50]
        :param minimum_should_match: Optional, minimum number of clauses that must match. [default: None]
        :param analyzer: Optional, analyzer to use for the query string. [default: None]
        :param auto_generate_synonyms_phrase_query: Optional, whether to automatically generate synonyms phrases. [default: True]
        :param boost: Optional, boost value for the query. [default: 1.0]
        :param lenient: Optional, whether to ignore format-based errors. [default: False]
        :param _name: Optional, name for the query. [default: None]
        """
        super().__init__(boost, _name)
        self.field = field
        self.value = value
        self.operator = operator
        self.zero_terms_query = zero_terms_query
        self.fuzziness = fuzziness
        self.prefix_length = prefix_length
        self.max_expansions = max_expansions
        self.minimum_should_match = minimum_should_match
        self.analyzer = analyzer
        self.auto_generate_synonyms_phrase_query = (
            auto_generate_synonyms_phrase_query
        )
        self.lenient = lenient
        self.match_query = self._make_query()

    def to_query(self):
        return self.match_query

    def _make_query(self):
        match_subquery = {"query": self.value}

        if self.operator:
            match_subquery["operator"] = self.operator
        if self.zero_terms_query:
            match_subquery["zero_terms_query"] = self.zero_terms_query
        if self.fuzziness:
            match_subquery["fuzziness"] = self.fuzziness
        if self.prefix_length:
            match_subquery["prefix_length"] = self.prefix_length
        if self.max_expansions:
            match_subquery["max_expansions"] = self.max_expansions
        if self.minimum_should_match:
            match_subquery["minimum_should_match"] = self.minimum_should_match
        if self.analyzer:
            match_subquery["analyzer"] = self.analyzer
        if self.auto_generate_synonyms_phrase_query is not None:
            match_subquery["auto_generate_synonyms_phrase_query"] = (
                self.auto_generate_synonyms_phrase_query
            )
        if self.boost:
            match_subquery["boost"] = self.boost
        if self.lenient is not None:
            match_subquery["lenient"] = self.lenient
        if self.name:
            match_subquery["_name"] = self.name

        match_query = {"match": {self.field: match_subquery}}
        return match_query


class MultiMatchQuery(FilterDSL):
    def __init__(
        self,
        query: str,
        fields: t.List[str],
        type: t.Optional[str] = None,
        operator: t.Optional[str] = None,
        minimum_should_match: t.Optional[t.Union[str, int]] = None,
        fuzziness: t.Optional[t.Union[str, int]] = None,
        prefix_length: t.Optional[int] = None,
        max_expansions: t.Optional[int] = None,
        analyzer: t.Optional[str] = None,
        slop: t.Optional[int] = None,
        boost: t.Optional[float] = None,
        tie_breaker: t.Optional[float] = None,
        auto_generate_synonyms_phrase_query: t.Optional[bool] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a MultiMatchQuery object.

        Use Cases:
        - Perform a full-text search across multiple fields.

        Args:
            :param query (str): The query string to search for.
            :param fields (list of str): The list of fields to search across.
            :param type (str, optional): The type of multi-match query, such as 'best_fields', 'most_fields', etc. [default: 'best_fields']
            :param operator (str, optional): The operator to use, either 'and' or 'or'. [default: 'or']
            :param minimum_should_match (str | int, optional): The minimum number of fields that should match. [default: None]
            :param fuzziness (str | int, optional): The fuzziness level for the query. [default: None]
            :param prefix_length (int, optional): The length of the prefix for fuzzy matching. [default: 0]
            :param max_expansions (int, optional): The maximum number of fuzzy expansions. [default: 50]
            :param analyzer (str, optional): The analyzer to use for the query. [default: None]
            :param slop (int, optional): The number of positions allowed between matching terms. [default: 0]
            :param boost (float, optional): The boost value for the query. [default: 1.0]
            :param tie_breaker (float, optional): How much to reduce the score of the less relevant documents in `most_fields` type. [default: 0.0]
            :param auto_generate_synonyms_phrase_query (bool, optional): Whether to automatically generate synonyms for phrase queries. [default: True]
            :param _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost, _name)
        self.query = query
        self.fields = fields
        self.type = type
        self.operator = operator
        self.minimum_should_match = minimum_should_match
        self.fuzziness = fuzziness
        self.prefix_length = prefix_length
        self.max_expansions = max_expansions
        self.analyzer = analyzer
        self.slop = slop
        self.tie_breaker = tie_breaker
        self.auto_generate_synonyms_phrase_query = (
            auto_generate_synonyms_phrase_query
        )
        self.multi_match_query = self._make_query()

    def to_query(self):
        return self.multi_match_query

    def _make_query(self):
        multi_match_subquery = {
            "query": self.query,
            "fields": self.fields,
        }

        if self.type:
            multi_match_subquery["type"] = self.type
        if self.operator:
            multi_match_subquery["operator"] = self.operator
        if self.minimum_should_match is not None:
            multi_match_subquery["minimum_should_match"] = (
                self.minimum_should_match
            )
        if self.fuzziness is not None:
            multi_match_subquery["fuzziness"] = self.fuzziness
        if self.prefix_length is not None:
            multi_match_subquery["prefix_length"] = self.prefix_length
        if self.max_expansions is not None:
            multi_match_subquery["max_expansions"] = self.max_expansions
        if self.analyzer is not None:
            multi_match_subquery["analyzer"] = self.analyzer
        if self.slop is not None:
            multi_match_subquery["slop"] = self.slop
        if self.boost is not None:
            multi_match_subquery["boost"] = self.boost
        if self.tie_breaker is not None:
            multi_match_subquery["tie_breaker"] = self.tie_breaker
        if self.auto_generate_synonyms_phrase_query is not None:
            multi_match_subquery["auto_generate_synonyms_phrase_query"] = (
                self.auto_generate_synonyms_phrase_query
            )
        if self.name:
            multi_match_subquery["_name"] = self.name

        multi_match_query = {"multi_match": multi_match_subquery}
        return multi_match_query


class FuzzyQuery(FilterDSL):
    def __init__(
        self,
        field: str,
        value: t.Any,
        fuzziness: t.Optional[t.Union[str, int]] = None,
        prefix_length: t.Optional[int] = None,
        max_expansions: t.Optional[int] = None,
        transpositions: t.Optional[bool] = None,
        boost: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a FuzzyQuery object.

        Use Cases:
        - Perform searches that allow for typographical errors or approximate matches by using fuzziness.

        Args:
            field (str): The field to apply the fuzzy query on.
            value (Any): The value to search for, allowing for fuzziness.
            fuzziness (str | int, optional): Defines the fuzziness level (e.g., "AUTO", 1, 2). [default: AUTO]
            prefix_length (int, optional): The number of initial characters that must match exactly. [default: 0]
            max_expansions (int, optional): The maximum number of variations considered for fuzzy matching. [default: 50]
            transpositions (bool, optional): Whether to allow transpositions (swap of two adjacent characters). [default: True]
            boost (float, optional): Boost value to influence the relevance score of matching documents. [default: 1.0]
            _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost, _name)
        self.field = field
        self.value = value
        self.fuzziness = fuzziness
        self.prefix_length = prefix_length
        self.max_expansions = max_expansions
        self.transpositions = transpositions
        self.boost = boost
        self.fuzzy_query = self._make_query()

    def to_query(self):
        return self.fuzzy_query

    def _make_query(self):
        fuzzy_subquery = {"value": self.value}

        if self.fuzziness is not None:
            fuzzy_subquery["fuzziness"] = self.fuzziness
        if self.prefix_length is not None:
            fuzzy_subquery["prefix_length"] = self.prefix_length
        if self.max_expansions is not None:
            fuzzy_subquery["max_expansions"] = self.max_expansions
        if self.transpositions is not None:
            fuzzy_subquery["transpositions"] = self.transpositions
        if self.boost is not None:
            fuzzy_subquery["boost"] = self.boost
        if self.name:
            fuzzy_subquery["_name"] = self.name

        return {"fuzzy": {self.field: fuzzy_subquery}}


class TermQuery(FilterDSL):
    def __init__(
        self,
        field: str,
        value: t.Any,
        boost: t.Optional[float] = None,
        case_insensitive: t.Optional[bool] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a TermQuery object.

        :param field: The field to match against.
        :param value: The term value to match.
        :param boost: Optional, boost value for the query. [default: 1.0]
        :param case_insensitive: Optional, whether to make the query case-insensitive. [default: False]
        :param _name: Optional, name for the query. [default: None]
        """
        super().__init__(boost=boost, _name=_name)
        self.field = field
        self.value = value
        self.case_insensitive = case_insensitive
        self.term_query = self._make_query()

    def to_query(self):
        return self.term_query

    def _make_query(self):
        term_subquery = {"value": self.value}

        if self.boost is not None:
            term_subquery["boost"] = self.boost
        if self.case_insensitive is not None:
            term_subquery["case_insensitive"] = self.case_insensitive
        if self.name:
            term_subquery["_name"] = self.name
        term_query = {"term": {self.field: term_subquery}}
        return term_query


class TermsQuery(FilterDSL):
    def __init__(
        self,
        field: str,
        values: t.List[t.Any],
        boost: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a TermsQuery object.

        :param field: The field to match against.
        :param values: A list of terms to match.
        :param boost: Optional, boost value for the query. [default: 1.0]
        :param _name: Optional, name for the query. [default: None]
        """
        super().__init__(boost=boost, _name=_name)
        self.field = field
        self.values = values
        self.boost = boost
        self.terms_query = self._make_query()

    def to_query(self):
        return self.terms_query

    def _make_query(self):
        terms_subquery = {"terms": {self.field: self.values}}

        if self.boost is not None:
            terms_subquery["terms"]["boost"] = self.boost
        if self.name:
            terms_subquery["terms"]["_name"] = self.name

        return terms_subquery


class TermsSetQuery(FilterDSL):
    def __init__(
        self,
        field: str,
        terms: t.List[str],
        minimum_should_match_field: t.Optional[str] = None,
        minimum_should_match_script: t.Optional[t.Dict[str, t.Any]] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a TermsSetQuery object.

        Use Cases:
        - Match documents where a specified number of terms from a set must match the document's field.

        Args:
            field (str): The document field to apply the terms_set query on.
            terms (list of str): A list of terms to match against the field.
            minimum_should_match_field (str, optional): A field in the document specifying how many terms must match. [default: None]
            minimum_should_match_script (dict, optional): A script defining custom logic for how many terms should match. [default: None]
            _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost=None, _name=_name)
        self.field = field
        self.terms = terms
        self.minimum_should_match_field = minimum_should_match_field
        self.minimum_should_match_script = minimum_should_match_script
        self.terms_set_query = self._make_query()

    def to_query(self):
        return self.terms_set_query

    def _make_query(self):
        terms_set_subquery = {"terms": self.terms}

        if self.minimum_should_match_field is not None:
            terms_set_subquery["minimum_should_match_field"] = (
                self.minimum_should_match_field
            )
        if self.minimum_should_match_script is not None:
            terms_set_subquery["minimum_should_match_script"] = (
                self.minimum_should_match_script
            )
        if self.name:
            terms_set_subquery["_name"] = self.name

        return {"terms_set": {self.field: terms_set_subquery}}


class ExistsQuery(FilterDSL):
    def __init__(
        self,
        field: str,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes an ExistsQuery object.

        :param field: The field to check for existence.
        :param _name: Optional, name for the query. [default: None]
        """
        super().__init__(boost=None, _name=_name)
        self.field = field
        self.exists_query = self._make_query()

    def to_query(self):
        return self.exists_query

    def _make_query(self):
        exists_subquery = {"field": self.field}

        if self.name:
            exists_subquery["_name"] = self.name

        exists_query = {"exists": exists_subquery}
        return exists_query


class NestedQuery(FilterDSL):
    def __init__(
        self,
        path: str,
        query: DSLQuery,
        score_mode: t.Optional[str] = None,
        ignore_unmapped: t.Optional[bool] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a NestedQuery object.

        :param path: The path to the nested object field.
        :param query: The query to apply to the nested documents.
        :param score_mode: Optional, how to combine scores from matching nested documents.
                           Options: 'avg', 'sum', 'max', 'min', 'none'. [default: 'none']
        :param ignore_unmapped: Optional, whether to ignore unmapped fields. [default: False]
        :param _name: Optional, name for the query. [default: None]
        """
        super().__init__(boost=None, _name=_name)
        self.path = path
        self.query = query
        self.score_mode = score_mode
        self.ignore_unmapped = ignore_unmapped
        self.nested_query = self._make_query()

    def to_query(self):
        return self.nested_query

    def _make_query(self):
        nested_subquery = {
            "path": self.path,
            "query": self.query.to_query(),
        }

        if self.score_mode is not None:
            nested_subquery["score_mode"] = self.score_mode
        if self.ignore_unmapped is not None:
            nested_subquery["ignore_unmapped"] = self.ignore_unmapped
        if self.name:
            nested_subquery["_name"] = self.name

        nested_query = {"nested": nested_subquery}
        return nested_query


class ScriptQuery(FilterDSL):
    def __init__(
        self,
        script: str,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        lang: t.Optional[str] = None,
        boost: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a ScriptQuery object.

        Use Cases:
        - Match documents based on a custom script, allowing for complex and dynamic conditions.

        Args:
            script (str): The script to be executed to determine whether a document matches.
            params (dict, optional): A dictionary of parameters to pass to the script. [default: None]
            lang (str, optional): The scripting language to use, such as 'painless'. [default: 'painless']
            boost (float, optional): Boost value to influence the relevance score of matching documents. [default: 1.0]
            _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost, _name)
        self.script = script
        self.params = params
        self.lang = lang
        self.script_query = self._make_query()

    def to_query(self):
        return self.script_query

    def _make_query(self):
        script_subquery = {"script": {"source": self.script}}

        if self.params:
            script_subquery["script"]["params"] = self.params
        if self.lang:
            script_subquery["script"]["lang"] = self.lang
        else:
            script_subquery["script"]["lang"] = "painless"
        if self.boost is not None:
            script_subquery["boost"] = self.boost
        if self.name:
            script_subquery["_name"] = self.name

        return {"script": script_subquery}


class RangeQuery(FilterDSL):
    def __init__(
        self,
        field: str,
        gte: t.Optional[t.Any] = None,
        lte: t.Optional[t.Any] = None,
        gt: t.Optional[t.Any] = None,
        lt: t.Optional[t.Any] = None,
        format: t.Optional[str] = None,
        time_zone: t.Optional[str] = None,
        relation: t.Optional[str] = None,
        boost: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a RangeQuery object.

        Use Cases:
        - Query documents where a field's value falls within a specific range.

        Args:
            field (str): The field to apply the range query on.
            gte (Any, optional): Matches values greater than or equal to this value. [default: None]
            lte (Any, optional): Matches values less than or equal to this value. [default: None]
            gt (Any, optional): Matches values greater than this value. [default: None]
            lt (Any, optional): Matches values less than this value. [default: None]
            format (str, optional): The format of the values if they are date/time types. [default: None]
            time_zone (str, optional): The time zone to use when parsing dates. [default: None]
            relation (str, optional): Defines how to match the range with the field. Options are 'within', 'contains', 'intersects'. [default: None]
            boost (float, optional): Boost value to influence the relevance score of matching documents. [default: 1.0]
            _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost, _name)
        self.field = field
        self.gte = gte
        self.lte = lte
        self.gt = gt
        self.lt = lt
        self.format = format
        self.time_zone = time_zone
        self.relation = relation
        self.boost = boost
        self.range_query = self._make_query()

    def to_query(self):
        return self.range_query

    def _make_query(self):
        range_subquery = {}

        if self.gte is not None:
            range_subquery["gte"] = self.gte
        if self.lte is not None:
            range_subquery["lte"] = self.lte
        if self.gt is not None:
            range_subquery["gt"] = self.gt
        if self.lt is not None:
            range_subquery["lt"] = self.lt
        if self.format is not None:
            range_subquery["format"] = self.format
        if self.time_zone is not None:
            range_subquery["time_zone"] = self.time_zone
        if self.relation is not None:
            range_subquery["relation"] = self.relation
        if self.boost is not None:
            range_subquery["boost"] = self.boost
        if self.name:
            range_subquery["_name"] = self.name

        return {"range": {self.field: range_subquery}}


class GeoDistanceQuery(FilterDSL):
    def __init__(
        self,
        field: str,
        distance: str,
        location: t.Dict[str, float],
        distance_type: t.Optional[str] = None,
        validation_method: t.Optional[str] = None,
        boost: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a GeoDistanceQuery object.

        Use Cases:
        - Filter documents by geographical distance from a given point.

        Args:
            field (str): The field containing the geo_point.
            distance (str): The radius distance from the location (e.g., "10km").
            location (dict): A dictionary with 'lat' and 'lon' as keys.
            distance_type (str, optional): How to compute the distance ('arc', 'plane'). [default: 'arc']
            validation_method (str, optional): Specifies how to validate the geo_point. [default: 'STRICT']
            boost (float, optional): Boost value to influence the relevance score. [default: 1.0]
            _name (str, optional): The name for the query. [default: None]
        """
        super().__init__(boost, _name)
        self.field = field
        self.distance = distance
        self.location = location
        self.distance_type = distance_type
        self.validation_method = validation_method
        self.boost = boost
        self.geo_distance_query = self._make_query()

    def to_query(self):
        return self.geo_distance_query

    def _make_query(self):
        geo_distance_subquery = {
            "distance": self.distance,
            self.field: self.location,
        }

        if self.distance_type is not None:
            geo_distance_subquery["distance_type"] = self.distance_type
        if self.validation_method is not None:
            geo_distance_subquery["validation_method"] = self.validation_method
        if self.boost is not None:
            geo_distance_subquery["boost"] = self.boost
        if self.name:
            geo_distance_subquery["_name"] = self.name

        return {"geo_distance": geo_distance_subquery}


class QueryStringQuery(FilterDSL):
    def __init__(
        self,
        query: str,
        default_field: t.Optional[str] = None,
        fields: t.Optional[t.List[str]] = None,
        type: t.Optional[str] = None,
        allow_leading_wildcard: t.Optional[bool] = None,
        analyze_wildcard: t.Optional[bool] = None,
        analyzer: t.Optional[str] = None,
        auto_generate_synonyms_phrase_query: t.Optional[bool] = None,
        default_operator: t.Optional[str] = None,
        enable_position_increments: t.Optional[bool] = None,
        fuzziness: t.Optional[t.Union[str, int]] = None,
        fuzzy_max_expansions: t.Optional[int] = None,
        fuzzy_prefix_length: t.Optional[int] = None,
        fuzzy_transpositions: t.Optional[bool] = None,
        lenient: t.Optional[bool] = None,
        max_determinized_states: t.Optional[int] = None,
        minimum_should_match: t.Optional[t.Union[str, int]] = None,
        quote_analyzer: t.Optional[str] = None,
        phrase_slop: t.Optional[int] = None,
        quote_field_suffix: t.Optional[str] = None,
        rewrite: t.Optional[str] = None,
        time_zone: t.Optional[str] = None,
        boost: t.Optional[float] = None,
        _name: t.Optional[str] = None,
    ):
        """
        Initializes a QueryStringQuery object.

        Use Cases:
        - Provides a way to use Lucene query syntax for complex queries
        - Allows searching across multiple fields with different boosts
        - Supports wildcards, fuzzy matching, regular expressions, and range queries

        Args:
            query (str): The query string in Lucene syntax
            default_field (str, optional): The default field to search if no field is specified
            fields (List[str], optional): List of fields to search in
            type (str, optional): The type of query ('best_fields', 'most_fields', 'cross_fields', etc.)
            allow_leading_wildcard (bool, optional): Whether to allow wildcards at start of word
            analyze_wildcard (bool, optional): Whether to analyze wildcard terms
            analyzer (str, optional): The analyzer to use for the query string
            auto_generate_synonyms_phrase_query (bool, optional): Whether to auto-generate phrase queries for synonyms
            default_operator (str, optional): The default operator ('AND' or 'OR')
            enable_position_increments (bool, optional): Whether to enable position increments in result queries
            fuzziness (str | int, optional): Fuzziness parameter for fuzzy queries
            fuzzy_max_expansions (int, optional): Maximum expansions for fuzzy queries
            fuzzy_prefix_length (int, optional): Length of prefix not checked for fuzziness
            fuzzy_transpositions (bool, optional): Whether to include transpositions for fuzzy queries
            lenient (bool, optional): Whether to ignore format-based failures
            max_determinized_states (int, optional): Maximum states a regex query can use
            minimum_should_match (str | int, optional): Minimum number of clauses that must match
            quote_analyzer (str, optional): Analyzer for quoted phrases
            phrase_slop (int, optional): Maximum number of positions allowed between matching tokens
            quote_field_suffix (str, optional): Suffix to append to fields for exact quoted matches
            rewrite (str, optional): Method used to rewrite the query
            time_zone (str, optional): Time zone to use for date/time fields
            boost (float, optional): Boost value for the query
            _name (str, optional): The name for the query
        """
        super().__init__(boost, _name)
        self.query = query
        self.default_field = default_field
        self.fields = fields
        self.type = type
        self.allow_leading_wildcard = allow_leading_wildcard
        self.analyze_wildcard = analyze_wildcard
        self.analyzer = analyzer
        self.auto_generate_synonyms_phrase_query = (
            auto_generate_synonyms_phrase_query
        )
        self.default_operator = default_operator
        self.enable_position_increments = enable_position_increments
        self.fuzziness = fuzziness
        self.fuzzy_max_expansions = fuzzy_max_expansions
        self.fuzzy_prefix_length = fuzzy_prefix_length
        self.fuzzy_transpositions = fuzzy_transpositions
        self.lenient = lenient
        self.max_determinized_states = max_determinized_states
        self.minimum_should_match = minimum_should_match
        self.quote_analyzer = quote_analyzer
        self.phrase_slop = phrase_slop
        self.quote_field_suffix = quote_field_suffix
        self.rewrite = rewrite
        self.time_zone = time_zone
        self.query_string_query = self._make_query()

    def to_query(self):
        return self.query_string_query

    def _make_query(self):  # noqa: C901
        query_string_subquery = {"query": self.query}

        if self.default_field:
            query_string_subquery["default_field"] = self.default_field
        if self.fields:
            query_string_subquery["fields"] = self.fields
        if self.type:
            query_string_subquery["type"] = self.type
        if self.allow_leading_wildcard is not None:
            query_string_subquery["allow_leading_wildcard"] = (
                self.allow_leading_wildcard
            )
        if self.analyze_wildcard is not None:
            query_string_subquery["analyze_wildcard"] = self.analyze_wildcard
        if self.analyzer:
            query_string_subquery["analyzer"] = self.analyzer
        if self.auto_generate_synonyms_phrase_query is not None:
            query_string_subquery["auto_generate_synonyms_phrase_query"] = (
                self.auto_generate_synonyms_phrase_query
            )
        if self.default_operator:
            query_string_subquery["default_operator"] = self.default_operator
        if self.enable_position_increments is not None:
            query_string_subquery["enable_position_increments"] = (
                self.enable_position_increments
            )
        if self.fuzziness is not None:
            query_string_subquery["fuzziness"] = self.fuzziness
        if self.fuzzy_max_expansions is not None:
            query_string_subquery["fuzzy_max_expansions"] = (
                self.fuzzy_max_expansions
            )
        if self.fuzzy_prefix_length is not None:
            query_string_subquery["fuzzy_prefix_length"] = (
                self.fuzzy_prefix_length
            )
        if self.fuzzy_transpositions is not None:
            query_string_subquery["fuzzy_transpositions"] = (
                self.fuzzy_transpositions
            )
        if self.lenient is not None:
            query_string_subquery["lenient"] = self.lenient
        if self.max_determinized_states is not None:
            query_string_subquery["max_determinized_states"] = (
                self.max_determinized_states
            )
        if self.minimum_should_match is not None:
            query_string_subquery["minimum_should_match"] = (
                self.minimum_should_match
            )
        if self.quote_analyzer:
            query_string_subquery["quote_analyzer"] = self.quote_analyzer
        if self.phrase_slop is not None:
            query_string_subquery["phrase_slop"] = self.phrase_slop
        if self.quote_field_suffix:
            query_string_subquery["quote_field_suffix"] = (
                self.quote_field_suffix
            )
        if self.rewrite:
            query_string_subquery["rewrite"] = self.rewrite
        if self.time_zone:
            query_string_subquery["time_zone"] = self.time_zone
        if self.boost is not None:
            query_string_subquery["boost"] = self.boost
        if self.name:
            query_string_subquery["_name"] = self.name

        return {"query_string": query_string_subquery}
