import unittest
from elasticquerydsl.base import (
    DSLQuery,
    BoolQuery,
    BoolShould,
    BoolMust,
    BoolMustNot,
    BoolFilter,
    LogicalDSL,
)


class DummyQuery(DSLQuery):
    def __init__(self, content, boost=None, _name=None):
        super().__init__(boost, _name)
        self.content = content

    def _make_query(self):
        query = {"dummy": self.content}
        if self.boost:
            query["boost"] = self.boost
        if self.name:
            query["_name"] = self.name
        return query


class TestLogicalDSL(unittest.TestCase):
    def test_bool_should(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query2")
        bool_should = BoolShould(query1, query2)
        expected = {
            "should": [
                {"dummy": "query1"},
                {"dummy": "query2"},
            ]
        }
        self.assertEqual(bool_should.to_query(), expected)

    def test_bool_must(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query2")
        bool_must = BoolMust(query1, query2)
        expected = {
            "must": [
                {"dummy": "query1"},
                {"dummy": "query2"},
            ]
        }
        self.assertEqual(bool_must.to_query(), expected)

    def test_bool_must_not(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query2")
        bool_must_not = BoolMustNot(query1, query2)
        expected = {
            "must_not": [
                {"dummy": "query1"},
                {"dummy": "query2"},
            ]
        }
        self.assertEqual(bool_must_not.to_query(), expected)

    def test_bool_filter(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query2")
        bool_filter = BoolFilter(query1, query2)
        expected = {
            "filter": [
                {"dummy": "query1"},
                {"dummy": "query2"},
            ]
        }
        self.assertEqual(bool_filter.to_query(), expected)

    def test_bool_query(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query2")
        bool_query = BoolQuery(
            must=BoolMust(query1),
            should=BoolShould(query2),
            boost=1.5,
            _name="bool_test",
        )
        expected = {
            "bool": {
                "must": [{"dummy": "query1"}],
                "should": [{"dummy": "query2"}],
                "boost": 1.5,
                "_name": "bool_test",
            }
        }
        self.assertEqual(bool_query.to_query(), expected)

    def test_logical_dsl_addition(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query2")
        query3 = DummyQuery(content="query3")

        must1 = BoolMust(query1)
        must2 = BoolMust(query2)
        combined_must = must1 + must2
        expected_must = {
            "must": [
                {"dummy": "query1"},
                {"dummy": "query2"},
            ]
        }
        self.assertEqual(combined_must.to_query(), expected_must)

        # Test adding a BoolMust and a single query
        must_with_query = must1 + query3
        expected_must_query = {
            "must": [
                {"dummy": "query1"},
                {"dummy": "query3"},
            ]
        }
        self.assertEqual(must_with_query.to_query(), expected_must_query)

    def test_logical_dsl_addition_incompatible_types(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query2")
        must = BoolMust(query1)
        should = BoolShould(query2)
        with self.assertRaises(NotImplementedError):
            _ = must + should

    def test_logical_dsl_addition_invalid_type(self):
        query1 = DummyQuery(content="query1")
        must = BoolMust(query1)
        with self.assertRaises(NotImplementedError):
            _ = must + "invalid"

    def test_bool_query_addition(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query2")
        bool_query1 = BoolQuery(must=BoolMust(query1))
        bool_query2 = BoolQuery(should=BoolShould(query2))
        combined_query = bool_query1 + bool_query2
        expected = {
            "bool": {
                "must": [{"dummy": "query1"}],
                "should": [{"dummy": "query2"}],
            }
        }
        self.assertEqual(combined_query.to_query(), expected)

    def test_bool_query_or(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query2")
        combined_query = query1 | query2
        expected = {
            "bool": {
                "should": [
                    {"dummy": "query1"},
                    {"dummy": "query2"},
                ]
            }
        }
        self.assertEqual(combined_query.to_query(), expected)

    def test_bool_query_and(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query2")
        combined_query = query1 & query2
        expected = {
            "bool": {
                "must": [
                    {"dummy": "query1"},
                    {"dummy": "query2"},
                ]
            }
        }
        self.assertEqual(combined_query.to_query(), expected)

    def test_bool_query_addition_invalid_type(self):
        query1 = DummyQuery(content="query1")
        bool_query = BoolQuery(must=BoolMust(query1))
        with self.assertRaises(NotImplementedError):
            _ = bool_query + "invalid"

    def test_bool_query_or_invalid_type(self):
        query1 = DummyQuery(content="query1")
        bool_query = BoolQuery(must=BoolMust(query1))
        with self.assertRaises(NotImplementedError):
            _ = bool_query | "invalid"

    def test_bool_query_invert(self):
        query1 = DummyQuery(content="query1")
        inverted_query = ~query1
        expected = {"bool": {"must_not": [{"dummy": "query1"}]}}
        self.assertEqual(inverted_query.to_query(), expected)

    def test_logical_dsl_clone(self):
        query1 = DummyQuery(content="query1")
        logical_dsl = LogicalDSL(query1)
        cloned_dsl = logical_dsl._clone()
        self.assertNotEqual(id(logical_dsl), id(cloned_dsl))
        self.assertEqual(logical_dsl.queries, cloned_dsl.queries)

    def test_dsl_query_equality(self):
        query1 = DummyQuery(content="query1")
        query2 = DummyQuery(content="query1")
        self.assertEqual(query1, query2)

        query3 = DummyQuery(content="query3")
        self.assertNotEqual(query1, query3)

    def test_dsl_query_repr(self):
        query = DummyQuery(content="query1", boost=1.5, _name="test_query")
        expected_repr = (
            "DummyQuery(boost=1.5 | name='test_query' | content='query1')"
        )
        self.assertEqual(expected_repr, repr(query))

    def test_dsl_query_to_query_not_implemented(self):
        class IncompleteQuery(DSLQuery):
            pass

        query = IncompleteQuery(boost=1.0, _name="incomplete")
        with self.assertRaises(NotImplementedError):
            query.to_query()


if __name__ == "__main__":
    unittest.main()
