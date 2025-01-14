import unittest
from elasticquerydsl.utils.booldslbuilder import BooleanDSLBuilder
from elasticquerydsl.filter import MatchQuery, TermQuery


class TestBooleanDSLBuilder(unittest.TestCase):
    def test_builder_empty(self):
        """
        Test building a BoolQuery without adding any clauses.
        Should raise an AttributeError since all boolean params cannot be None.
        """
        builder = BooleanDSLBuilder()
        with self.assertRaises(AttributeError):
            builder.build()

    def test_builder_with_must(self):
        """
        Test building a BoolQuery with a single 'must' clause.
        """
        builder = BooleanDSLBuilder()
        match_query = MatchQuery(field="title", value="python")
        builder.add_must_query(match_query)
        bool_query = builder.build()
        expected = {
            "bool": {"must": [{"match": {"title": {"query": "python"}}}]}
        }
        self.assertEqual(bool_query.to_query(), expected)

    def test_builder_with_should(self):
        """
        Test building a BoolQuery with a single 'should' clause.
        """
        builder = BooleanDSLBuilder()
        match_query = MatchQuery(field="content", value="elasticsearch")
        builder.add_should_query(match_query)
        bool_query = builder.build()
        expected = {
            "bool": {
                "should": [{"match": {"content": {"query": "elasticsearch"}}}]
            }
        }
        self.assertEqual(bool_query.to_query(), expected)

    def test_builder_with_must_and_should(self):
        """
        Test building a BoolQuery with both 'must' and 'should' clauses.
        """
        builder = BooleanDSLBuilder()
        must_query = MatchQuery(field="title", value="python")
        should_query = MatchQuery(field="content", value="elasticsearch")
        builder.add_must_query(must_query)
        builder.add_should_query(should_query)
        bool_query = builder.build()
        expected = {
            "bool": {
                "must": [{"match": {"title": {"query": "python"}}}],
                "should": [{"match": {"content": {"query": "elasticsearch"}}}],
            }
        }
        self.assertEqual(bool_query.to_query(), expected)

    def test_builder_with_all_clauses(self):
        """
        Test building a BoolQuery with 'must', 'should', 'must_not', and 'filter' clauses.
        Also test setting the 'boost' and '_name' parameters.
        """
        builder = BooleanDSLBuilder()
        must_query = MatchQuery(field="title", value="python")
        should_query = MatchQuery(field="content", value="elasticsearch")
        must_not_query = TermQuery(field="status", value="deprecated")
        filter_query = TermQuery(field="author", value="john")
        builder.add_must_query(must_query)
        builder.add_should_query(should_query)
        builder.add_must_not_query(must_not_query)
        builder.add_filter_query(filter_query)
        builder.set_boost(1.5)
        builder.set_name("complex_query")
        bool_query = builder.build()
        expected = {
            "bool": {
                "must": [{"match": {"title": {"query": "python"}}}],
                "should": [{"match": {"content": {"query": "elasticsearch"}}}],
                "must_not": [{"term": {"status": {"value": "deprecated"}}}],
                "filter": [{"term": {"author": {"value": "john"}}}],
                "boost": 1.5,
                "_name": "complex_query",
            }
        }
        self.assertEqual(bool_query.to_query(), expected)

    def test_builder_multiple_queries(self):
        """
        Test adding multiple queries at once to the same clause.
        """
        builder = BooleanDSLBuilder()
        must_query1 = MatchQuery(field="title", value="python")
        must_query2 = MatchQuery(field="title", value="elasticsearch")
        builder.add_must_query(must_query1, must_query2)
        bool_query = builder.build()
        expected = {
            "bool": {
                "must": [
                    {"match": {"title": {"query": "python"}}},
                    {"match": {"title": {"query": "elasticsearch"}}},
                ]
            }
        }
        self.assertEqual(bool_query.to_query(), expected)

    def test_builder_chained_methods(self):
        """
        Test chaining method calls to build a BoolQuery.
        """
        builder = BooleanDSLBuilder()
        builder.set_name("chained_query").set_boost(2.0)
        must_query = MatchQuery(field="title", value="python")
        builder.add_must_query(must_query)
        bool_query = builder.build()
        expected = {
            "bool": {
                "must": [{"match": {"title": {"query": "python"}}}],
                "boost": 2.0,
                "_name": "chained_query",
            }
        }
        self.assertEqual(bool_query.to_query(), expected)

    def test_builder_with_no_clauses(self):
        """
        Test that building a BoolQuery without any clauses raises an error.
        """
        builder = BooleanDSLBuilder()
        with self.assertRaises(AttributeError):
            builder.build()

    def test_builder_reset(self):
        """
        Test that the builder can be reused after building a query.
        """
        builder = BooleanDSLBuilder()
        must_query = MatchQuery(field="title", value="python")
        builder.add_must_query(must_query)
        bool_query1 = builder.build()
        expected1 = {
            "bool": {"must": [{"match": {"title": {"query": "python"}}}]}
        }
        self.assertEqual(bool_query1.to_query(), expected1)

        # Reset builder for a new query
        builder = BooleanDSLBuilder()
        should_query = MatchQuery(field="content", value="elasticsearch")
        builder.add_should_query(should_query)
        bool_query2 = builder.build()
        expected2 = {
            "bool": {
                "should": [{"match": {"content": {"query": "elasticsearch"}}}]
            }
        }
        self.assertEqual(bool_query2.to_query(), expected2)


if __name__ == "__main__":
    unittest.main()
