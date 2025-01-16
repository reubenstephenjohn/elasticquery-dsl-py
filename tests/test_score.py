import unittest
from elasticquerydsl.filter import MatchQuery
from elasticquerydsl.score import (
    ConstantScoreQuery,
    FunctionScoreQuery,
    ScriptScoreFunction,
    RandomScoreFunction,
    FieldValueFactorFunction,
    DecayFunction,
    WeightFunction,
)


class TestScoreDSL(unittest.TestCase):
    def test_constant_score_query(self):
        # Basic constant score query
        filter_query = MatchQuery(field="status", value="active")
        query = ConstantScoreQuery(filter_query=filter_query)
        expected = {
            "constant_score": {
                "filter": {"match": {"status": {"query": "active"}}}
            }
        }
        self.assertEqual(query.to_query(), expected)

        # Constant score query with boost and name
        query = ConstantScoreQuery(
            filter_query=filter_query, boost=1.5, _name="constant_score_test"
        )
        expected = {
            "constant_score": {
                "filter": {"match": {"status": {"query": "active"}}},
                "boost": 1.5,
                "_name": "constant_score_test",
            }
        }
        self.assertEqual(query.to_query(), expected)

    def test_function_score_query(self):
        # Basic function score query
        base_query = MatchQuery(field="title", value="python")
        script_function = ScriptScoreFunction(
            script="doc['likes'].value / 10",
            params={"factor": 1.2},
            weight=1.5,
        )
        query = FunctionScoreQuery(
            query=base_query, functions=[script_function]
        )
        expected = {
            "function_score": {
                "query": {"match": {"title": {"query": "python"}}},
                "functions": [
                    {
                        "script_score": {
                            "script": {
                                "source": "doc['likes'].value / 10",
                                "params": {"factor": 1.2},
                            }
                        },
                        "weight": 1.5,
                    }
                ],
            }
        }
        self.assertEqual(query.to_query(), expected)

        # Complex function score query with multiple functions and parameters
        random_function = RandomScoreFunction(seed=42, weight=0.8)
        field_factor_function = FieldValueFactorFunction(
            field="popularity", factor=1.2, modifier="log1p", weight=1.3
        )
        decay_function = DecayFunction(
            decay_type="gauss",
            field="date",
            origin="2023-01-01",
            scale="30d",
            weight=0.9,
        )
        weight_function = WeightFunction(weight=2.0)

        query = FunctionScoreQuery(
            query=base_query,
            functions=[
                script_function,
                random_function,
                field_factor_function,
                decay_function,
                weight_function,
            ],
            score_mode="sum",
            boost_mode="multiply",
            max_boost=3.0,
            min_score=0.5,
            _name="function_score_test",
        )
        expected = {
            "function_score": {
                "query": {"match": {"title": {"query": "python"}}},
                "functions": [
                    {
                        "script_score": {
                            "script": {
                                "source": "doc['likes'].value / 10",
                                "params": {"factor": 1.2},
                            }
                        },
                        "weight": 1.5,
                    },
                    {"random_score": {"seed": 42}, "weight": 0.8},
                    {
                        "field_value_factor": {
                            "field": "popularity",
                            "factor": 1.2,
                            "modifier": "log1p",
                        },
                        "weight": 1.3,
                    },
                    {
                        "gauss": {
                            "date": {"origin": "2023-01-01", "scale": "30d"}
                        },
                        "weight": 0.9,
                    },
                    {"weight": 2.0},
                ],
                "score_mode": "sum",
                "boost_mode": "multiply",
                "max_boost": 3.0,
                "min_score": 0.5,
                "_name": "function_score_test",
            }
        }
        self.assertEqual(query.to_query(), expected)
