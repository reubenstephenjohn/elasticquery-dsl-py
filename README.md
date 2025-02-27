# elasticquery-dsl-py

[![PyPI version](https://img.shields.io/pypi/v/elasticquery-dsl-py.svg)](https://pypi.org/project/elasticquery-dsl-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/elasticquery-dsl-py.svg)](https://pypi.org/project/elasticquery-dsl-py/)
[![License](https://img.shields.io/github/license/workindia/elasticquery-dsl-py.svg)](https://github.com/workindia/elasticquery-dsl-py/blob/main/LICENSE)

A Python-based Domain Specific Language (DSL) for building and managing Elasticsearch queries.
This library aims to simplify the process of constructing complex Elasticsearch queries by providing an intuitive and readable syntax.

## Features

- Build complex Elasticsearch queries using a clean, Pythonic interface
- Combine queries using logical operators (`&`, `|`, `~`)
- Support for a wide range of Elasticsearch query types
- Type hints for better IDE integration and code completion
- Fluent interface for building complex boolean queries
- Support for scoring functions and boosting

## Installation

You can install elasticquery-dsl-py from PyPI:

```bash
pip install elasticquery-dsl-py
```

## Quick Start

Here's a simple example to get you started with elasticquery-dsl-py:

```python
from elasticquerydsl.filter import MatchQuery, RangeQuery

# Create a simple match query
title_query = MatchQuery(field="title", value="python")

# Create a range query
date_query = RangeQuery(field="created_at", gte="2023-01-01", lte="2023-12-31")

# Combine queries using logical operators
combined_query = title_query & date_query

# Get the Elasticsearch query dict
query_dict = combined_query.to_query()
print(query_dict)
```
This will output a query that matches documents with "python" in the title field and a creation date within 2023:

```json
{
  "bool": {
    "must": [
      {"match": {"title": {"query": "python"}}},
      {"range": {"created_at": {"gte": "2023-01-01", "lte": "2023-12-31"}}}
    ]
  }
}
```

## Usage Examples

### Basic Queries

Let's explore some basic query types:

```python
from elasticquerydsl.filter import (
    MatchAllQuery,
    MatchNoneQuery,
    MatchQuery,
    MultiMatchQuery,
    RangeQuery,
    GeoDistanceQuery,
    QueryStringQuery
)

# Match all documents
match_all = MatchAllQuery()
print("Match All Query:")
print(match_all.to_query())

# Match no documents
match_none = MatchNoneQuery()
print("Match None Query:")
print(match_none.to_query())

# Match query with fuzziness
fuzzy_match = MatchQuery(
    field="description",
    value="programming",
    fuzziness="AUTO",
    boost=2.0
)
print("Fuzzy Match Query:")
print(fuzzy_match.to_query())

# Multi-match query across multiple fields
multi_match = MultiMatchQuery(
    query="python elasticsearch",
    fields=["title", "description", "tags"],
    type="best_fields"
)
print("Multi-Match Query:")
print(multi_match.to_query())
```

### Range and Geo Queries

```python
# Range query for numeric values
price_range = RangeQuery(
    field="price",
    gte=10,
    lte=100
)
print("Price Range Query:")
print(price_range.to_query())

# Date range query with formatting
date_range = RangeQuery(
    field="created_at",
    gte="2023-01-01",
    lte="now",
    format="yyyy-MM-dd||yyyy"
)
print("Date Range Query:")
print(date_range.to_query())

# Geo-distance query
geo_query = GeoDistanceQuery(
    field="location",
    distance="10km",
    location={"lat": 40.7128, "lon": -74.0060}  # New York City coordinates
)
print("Geo Distance Query:")
print(geo_query.to_query())
```

### Query String and Complex Queries

```python
# Query string query (Lucene syntax)
query_string = QueryStringQuery(
    query="(python OR java) AND framework",
    fields=["title^2", "description"],  # Boost title field
    default_operator="AND"
)
print("Query String Query:")
print(query_string.to_query())
```

### Combining Queries with Logical Operators

elasticquery-dsl-py allows you to combine queries using logical operators:

```python
# AND operator (&)
title_query = MatchQuery(field="title", value="python")
price_query = RangeQuery(field="price", lte=50)
and_query = title_query & price_query
print("AND Query:")
print(and_query.to_query())

# OR operator (|)
python_query = MatchQuery(field="language", value="python")
java_query = MatchQuery(field="language", value="java")
or_query = python_query | java_query
print("OR Query:")
print(or_query.to_query())

# NOT operator (~)
not_query = ~MatchQuery(field="status", value="deprecated")
print("NOT Query:")
print(not_query.to_query())

# Complex combination
complex_query = (python_query | java_query) & price_query & ~MatchQuery(field="status", value="archived")
print("Complex Combined Query:")
print(complex_query.to_query())
```

### Using the Boolean DSL Builder

For more complex boolean queries, you can use the `BooleanDSLBuilder` class:

```python
from elasticquerydsl.utils.booldslbuilder import BooleanDSLBuilder
from elasticquerydsl.filter import MatchQuery, RangeQuery

# Create queries
title_query = MatchQuery(field="title", value="elasticsearch")
description_query = MatchQuery(field="description", value="python")
price_query = RangeQuery(field="price", gte=10, lte=100)
status_query = MatchQuery(field="status", value="active")
premium_query = MatchQuery(field="premium", value=True)

# Build a complex boolean query
bool_query = BooleanDSLBuilder() \
    .add_must_query(title_query, status_query) \
    .add_should_query(description_query, premium_query) \
    .add_filter_query(price_query) \
    .add_must_not_query(MatchQuery(field="archived", value=True)) \
    .set_boost(1.5) \
    .set_name("product_search") \
    .build()

print("Boolean DSL Builder Query:")
print(bool_query.to_query())
```

### Scoring Functions

elasticquery-dsl-py supports various scoring functions to influence document relevance:

```python
from elasticquerydsl.score import (
    ConstantScoreQuery,
    FunctionScoreQuery,
    ScriptScoreFunction,
    RandomScoreFunction,
    FieldValueFactorFunction,
    DecayFunction,
    WeightFunction
)

# Constant score query
const_score = ConstantScoreQuery(
    filter_query=MatchQuery(field="category", value="electronics"),
    boost=1.2
)
print("Constant Score Query:")
print(const_score.to_query())

# Function score query with multiple functions
base_query = MatchQuery(field="title", value="python")

# Script score function
script_function = ScriptScoreFunction(
    script="doc['likes'].value / 10",
    params={"factor": 1.2},
    weight=1.5
)

# Random score function
random_function = RandomScoreFunction(seed=42, weight=0.8)

# Field value factor function
field_factor_function = FieldValueFactorFunction(
    field="popularity",
    factor=1.2,
    modifier="log1p",
    weight=1.3
)

# Decay function for time-based scoring
decay_function = DecayFunction(
    decay_type="gauss",
    field="date",
    origin="2023-01-01",
    scale="30d",
    weight=0.9
)

# Weight function
weight_function = WeightFunction(weight=2.0)

# Combine all functions in a function score query
function_score_query = FunctionScoreQuery(
    query=base_query,
    functions=[
        script_function,
        random_function,
        field_factor_function,
        decay_function,
        weight_function
    ],
    score_mode="sum",
    boost_mode="multiply",
    max_boost=3.0,
    min_score=0.5,
    _name="function_score_test"
)

print("Function Score Query:")
print(function_score_query.to_query())
```

## Integration with Elasticsearch

Here's how you can use elasticquery-dsl-py with the official Elasticsearch Python client:

```python
from elasticsearch import Elasticsearch
from elasticquerydsl.filter import MatchQuery, RangeQuery

# Create Elasticsearch client
es = Elasticsearch("http://localhost:9200")

# Build query using elasticquery-dsl-py
title_query = MatchQuery(field="title", value="python")
date_query = RangeQuery(field="created_at", gte="2023-01-01")
combined_query = title_query & date_query

# Execute search
response = es.search(
    index="my_index",
    body={
        "query": combined_query.to_query(),
        "size": 10
    }
)

# Process results
print(f"Found {response['hits']['total']['value']} documents")
for hit in response['hits']['hits']:
    print(f"Document ID: {hit['_id']}, Score: {hit['_score']}")
    print(f"Title: {hit['_source'].get('title')}")
    print("---")
```

## Development

### Setting Up Development Environment

To set up a development environment for elasticquery-dsl-py:

```bash
# Clone the repository
git clone https://github.com/workindia/elasticquery-dsl-py.git
cd elasticquery-dsl-py

# Initialize the development environment
make init

# Install the package in development mode
pip install -e .
```

### Running Tests

To run the tests:

```bash
# Run all tests
pytest

# Run tests with coverage | Requires `pytest-cov`
pytest --cov=elasticquerydsl
```

### Building the Package

To build the package:

```bash
make dist
```

### Making a Release

To make a release increment:

```bash
# For a patch release
make release PART=patch

# For a minor release
make release PART=minor

# For a major release
make release PART=major
```

## Contributing

Contributions are welcome! Here's how you can contribute to elasticquery-dsl-py:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-feature`
3. Make your changes and add tests
4. Run the tests to ensure they pass
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature/my-new-feature`
7. Submit a pull request

Please make sure your code follows the project's coding style and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Inspired by the Elasticsearch DSL query structure


## Contact

For questions or feedback, please open an issue on the [GitHub repository](https://github.com/workindia/elasticquery-dsl-py/issues).

## Changelog

Please find the changelog here: [CHANGELOG.md](CHANGELOG.md)

## Authors

`elasticquery-dsl-py` was written by [Nikhil Kumar](mailto:nikhil.kumar@workindia.in).
