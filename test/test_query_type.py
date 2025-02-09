import pytest

from sql_metadata import Parser, QueryType


def test_insert_query():
    queries = [
        "INSERT IGNORE /* foo */ INTO bar VALUES (1, '123', '2017-01-01');",
        "/* foo */ INSERT IGNORE INTO bar VALUES (1, '123', '2017-01-01');"
        "-- foo\nINSERT IGNORE INTO bar VALUES (1, '123', '2017-01-01');"
        "# foo\nINSERT IGNORE INTO bar VALUES (1, '123', '2017-01-01');",
    ]

    for query in queries:
        assert "INSERT" == Parser(query).query_type


def test_select_query():
    queries = [
        "SELECT /* foo */ foo FROM bar",
        "/* foo */ SELECT foo FROM bar"
        "-- foo\nSELECT foo FROM bar"
        "# foo\nSELECT foo FROM bar",
    ]

    for query in queries:
        assert "SELECT" == Parser(query).query_type


def test_unsupported_query():
    queries = [
        "FOO BAR",
        "DO SOMETHING",
    ]

    for query in queries:
        with pytest.raises(ValueError) as ex:
            _ = Parser(query).query_type

        assert "Not supported query type!" in str(ex.value)


def test_empty_query():
    queries = ["", "/* empty query */"]

    for query in queries:
        with pytest.raises(ValueError) as ex:
            _ = Parser(query).query_type

        assert "Empty queries are not supported!" in str(ex.value)


def test_redundant_parentheses():
    query = """
    (select c, d from ab)
    """
    parser = Parser(query)
    assert parser.query_type == QueryType.SELECT


def test_multiple_redundant_parentheses():
    query = """
    ((update ac set ab = 1))
    """
    parser = Parser(query)
    assert parser.query_type == QueryType.UPDATE


def test_multiple_redundant_parentheses_create():
    query = """
    ((create table aa (ac int primary key)))
    """
    parser = Parser(query)
    assert parser.query_type == QueryType.CREATE
