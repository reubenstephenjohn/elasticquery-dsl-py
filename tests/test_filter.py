import unittest
from elasticquerydsl.filter import (
    MatchAllQuery,
    MatchNoneQuery,
    MatchQuery,
    MultiMatchQuery,
    FuzzyQuery,
    TermQuery,
    TermsQuery,
    TermsSetQuery,
    ExistsQuery,
    NestedQuery,
    ScriptQuery,
    RangeQuery,
    GeoDistanceQuery,
    QueryStringQuery,
)


class TestFilterDSL(unittest.TestCase):
    def test_match_all_query(self):
        query = MatchAllQuery()
        expected = {"match_all": {}}
        self.assertEqual(query.to_query(), expected)

        query = MatchAllQuery(boost=1.2, _name="match_all_test")
        expected = {"match_all": {"boost": 1.2, "_name": "match_all_test"}}
        self.assertEqual(query.to_query(), expected)

    def test_match_none_query(self):
        query = MatchNoneQuery()
        expected = {"match_none": {}}
        self.assertEqual(query.to_query(), expected)

        query = MatchNoneQuery(_name="match_none_test")
        expected = {"match_none": {"_name": "match_none_test"}}
        self.assertEqual(query.to_query(), expected)

    def test_match_query(self):
        query = MatchQuery(field="title", value="python")
        expected = {"match": {"title": {"query": "python"}}}
        self.assertEqual(query.to_query(), expected)

        query = MatchQuery(
            field="title",
            value="python",
            operator="and",
            boost=2.0,
            _name="match_query_test",
        )
        expected = {
            "match": {
                "title": {
                    "query": "python",
                    "operator": "and",
                    "boost": 2.0,
                    "_name": "match_query_test",
                }
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_multi_match_query(self):
        query = MultiMatchQuery(query="python", fields=["title", "content"])
        expected = {
            "multi_match": {
                "query": "python",
                "fields": ["title", "content"],
            }
        }
        self.assertEqual(query.to_query(), expected)

        query = MultiMatchQuery(
            query="python",
            fields=["title", "content"],
            type="phrase",
            operator="and",
            boost=1.5,
            _name="multi_match_test",
        )
        expected = {
            "multi_match": {
                "query": "python",
                "fields": ["title", "content"],
                "type": "phrase",
                "operator": "and",
                "boost": 1.5,
                "_name": "multi_match_test",
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_fuzzy_query(self):
        query = FuzzyQuery(field="title", value="pythn")
        expected = {"fuzzy": {"title": {"value": "pythn"}}}
        self.assertEqual(query.to_query(), expected)

        query = FuzzyQuery(
            field="title",
            value="pythn",
            fuzziness="AUTO",
            max_expansions=10,
            boost=2.0,
            _name="fuzzy_test",
        )
        expected = {
            "fuzzy": {
                "title": {
                    "value": "pythn",
                    "fuzziness": "AUTO",
                    "max_expansions": 10,
                    "boost": 2.0,
                    "_name": "fuzzy_test",
                }
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_term_query(self):
        query = TermQuery(field="status", value="active")
        expected = {"term": {"status": {"value": "active"}}}
        self.assertEqual(query.to_query(), expected)

        query = TermQuery(
            field="status",
            value="active",
            boost=1.2,
            case_insensitive=True,
            _name="term_query_test",
        )
        expected = {
            "term": {
                "status": {
                    "value": "active",
                    "boost": 1.2,
                    "case_insensitive": True,
                    "_name": "term_query_test",
                }
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_terms_query(self):
        query = TermsQuery(field="tags", values=["python", "elasticsearch"])
        expected = {"terms": {"tags": ["python", "elasticsearch"]}}
        self.assertEqual(query.to_query(), expected)

        query = TermsQuery(
            field="tags",
            values=["python", "elasticsearch"],
            boost=1.5,
            _name="terms_query_test",
        )
        expected = {
            "terms": {
                "tags": ["python", "elasticsearch"],
                "boost": 1.5,
                "_name": "terms_query_test",
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_terms_set_query(self):
        query = TermsSetQuery(
            field="tags",
            terms=["python", "elasticsearch"],
            minimum_should_match_field="required_matches",
        )
        expected = {
            "terms_set": {
                "tags": {
                    "terms": ["python", "elasticsearch"],
                    "minimum_should_match_field": "required_matches",
                }
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_exists_query(self):
        query = ExistsQuery(field="user")
        expected = {"exists": {"field": "user"}}
        self.assertEqual(query.to_query(), expected)

        query = ExistsQuery(field="user", _name="exists_test")
        expected = {"exists": {"field": "user", "_name": "exists_test"}}
        self.assertEqual(query.to_query(), expected)

    def test_nested_query(self):
        inner_query = MatchQuery(field="comments.text", value="great")
        query = NestedQuery(path="comments", query=inner_query)
        expected = {
            "nested": {
                "path": "comments",
                "query": {"match": {"comments.text": {"query": "great"}}},
            }
        }
        self.assertEqual(query.to_query(), expected)

        query = NestedQuery(
            path="comments",
            query=inner_query,
            score_mode="avg",
            _name="nested_test",
        )
        expected = {
            "nested": {
                "path": "comments",
                "query": {"match": {"comments.text": {"query": "great"}}},
                "score_mode": "avg",
                "_name": "nested_test",
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_script_query(self):
        query = ScriptQuery(
            script="doc['num1'].value > params.param1", params={"param1": 5}
        )
        expected = {
            "script": {
                "script": {
                    "source": "doc['num1'].value > params.param1",
                    "params": {"param1": 5},
                    "lang": "painless",
                }
            }
        }
        self.assertEqual(query.to_query(), expected)

        query = ScriptQuery(
            script="doc['num1'].value > params.param1",
            params={"param1": 5},
            lang="painless",
            boost=1.5,
            _name="script_test",
        )
        expected = {
            "script": {
                "script": {
                    "source": "doc['num1'].value > params.param1",
                    "params": {"param1": 5},
                    "lang": "painless",
                },
                "boost": 1.5,
                "_name": "script_test",
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_range_query(self):
        query = RangeQuery(field="age", gte=10, lte=20)
        expected = {"range": {"age": {"gte": 10, "lte": 20}}}
        self.assertEqual(query.to_query(), expected)

        query = RangeQuery(
            field="date",
            gt="now-1d/d",
            lt="now/d",
            format="strict_date_optional_time",
            time_zone="+01:00",
            boost=2.0,
            _name="range_test",
        )
        expected = {
            "range": {
                "date": {
                    "gt": "now-1d/d",
                    "lt": "now/d",
                    "format": "strict_date_optional_time",
                    "time_zone": "+01:00",
                    "boost": 2.0,
                    "_name": "range_test",
                }
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_geo_distance_query(self):
        query = GeoDistanceQuery(
            field="location",
            distance="12km",
            location={"lat": 40.715, "lon": -74.011},
        )
        expected = {
            "geo_distance": {
                "distance": "12km",
                "location": {"lat": 40.715, "lon": -74.011},
            }
        }
        self.assertEqual(query.to_query(), expected)

        query = GeoDistanceQuery(
            field="location",
            distance="12km",
            location={"lat": 40.715, "lon": -74.011},
            distance_type="plane",
            validation_method="IGNORE_MALFORMED",
            boost=1.5,
            _name="geo_distance_test",
        )
        expected = {
            "geo_distance": {
                "distance": "12km",
                "location": {"lat": 40.715, "lon": -74.011},
                "distance_type": "plane",
                "validation_method": "IGNORE_MALFORMED",
                "boost": 1.5,
                "_name": "geo_distance_test",
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_query_string_query(self):
        # Basic query string test
        query = QueryStringQuery(query="python AND elasticsearch")
        expected = {"query_string": {"query": "python AND elasticsearch"}}
        self.assertEqual(query.to_query(), expected)

        # Complex query string test with all parameters
        query = QueryStringQuery(
            query='title:python AND (description:elasticsearch OR description:"search engine")',
            default_field="content",
            fields=["title^2", "description"],
            type="best_fields",
            allow_leading_wildcard=False,
            analyze_wildcard=True,
            analyzer="standard",
            auto_generate_synonyms_phrase_query=False,
            default_operator="AND",
            enable_position_increments=True,
            fuzziness="AUTO",
            fuzzy_max_expansions=50,
            fuzzy_prefix_length=2,
            fuzzy_transpositions=True,
            lenient=True,
            max_determinized_states=10000,
            minimum_should_match="75%",
            quote_analyzer="keyword",
            phrase_slop=2,
            quote_field_suffix=".exact",
            rewrite="constant_score",
            time_zone="+01:00",
            boost=1.5,
            _name="query_string_test",
        )
        expected = {
            "query_string": {
                "query": 'title:python AND (description:elasticsearch OR description:"search engine")',
                "default_field": "content",
                "fields": ["title^2", "description"],
                "type": "best_fields",
                "allow_leading_wildcard": False,
                "analyze_wildcard": True,
                "analyzer": "standard",
                "auto_generate_synonyms_phrase_query": False,
                "default_operator": "AND",
                "enable_position_increments": True,
                "fuzziness": "AUTO",
                "fuzzy_max_expansions": 50,
                "fuzzy_prefix_length": 2,
                "fuzzy_transpositions": True,
                "lenient": True,
                "max_determinized_states": 10000,
                "minimum_should_match": "75%",
                "quote_analyzer": "keyword",
                "phrase_slop": 2,
                "quote_field_suffix": ".exact",
                "rewrite": "constant_score",
                "time_zone": "+01:00",
                "boost": 1.5,
                "_name": "query_string_test",
            }
        }
        self.assertEqual(query.to_query(), expected)


if __name__ == "__main__":
    unittest.main()
