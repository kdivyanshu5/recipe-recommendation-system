"""Tests for the list-parsing helpers. These use only the standard library."""

from app.utils.parsing import parse_float_list, parse_list


def test_parse_python_list_string():
    assert parse_list("['garlic', 'salt']") == ["garlic", "salt"]


def test_parse_handles_none_and_empty():
    assert parse_list(None) == []
    assert parse_list("") == []


def test_parse_already_a_list():
    assert parse_list(["a", "b"]) == ["a", "b"]


def test_parse_comma_fallback():
    assert parse_list("garlic, salt, pepper") == ["garlic", "salt", "pepper"]


def test_parse_float_list():
    assert parse_float_list("[100.0, 5, 2.5]") == [100.0, 5.0, 2.5]


def test_parse_float_list_skips_bad_values():
    assert parse_float_list("['a', '2.0']") == [2.0]
