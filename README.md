# elasticquery-dsl-py

[![PyPI version](https://badge.fury.io/py/elasticquery-dsl-py.svg)](https://pypi.org/project/elasticquery-dsl-py/)

A Python library for building Elasticsearch queries using a fluent, domain-specific language (DSL). This library aims to simplify the process of constructing complex Elasticsearch queries by providing an intuitive and readable syntax.

## Usage

Here are some examples of how to use elasticquery-dsl-py to build Elasticsearch queries:

### Basic Queries

```python
from elasticquerydsl import MatchQuery, BoolQuery, RangeQuery, GeoDistanceQuery

# Match documents where the 'title' field contains the term 'python'
match_query = MatchQuery(field="title", value="python")

# Find documents where the 'age' field is greater than or equal to 30
range_query = RangeQuery(field="age", gte=30)

# Combine queries using boolean logic
bool_query = BoolQuery(must=[match_query, range_query])

# Create a geo-distance query to find documents within 10 kilometers of a given location
geo_query = GeoDistanceQuery(
    field="location", distance="10km", location={"lat": 28.6129, "lon": 77.2090}
)

# Convert the query to Elasticsearch JSON format
elasticsearch_query = bool_query.to_query()

# Print the Elasticsearch query
print(elasticsearch_query)
```

## Installation

Use the package manager [pip](https://pip.pypa.io/get-pip.py) to install elasticquery-dsl-py:

```bash
pip install elasticquery-dsl-py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss the proposed changes.

### Build Requirements

-   Make
-   Python

### Initialise Build Environment

One time initialisation

```
make init
```

## Changelog

Please find the changelog here: [CHANGELOG.md](CHANGELOG.md)

## Authors

`elasticquery-dsl-py` was written by [Nikhil Kumar](mailto:nikhil.kumar@workindia.in).
