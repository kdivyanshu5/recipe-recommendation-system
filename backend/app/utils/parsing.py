"""Helpers for turning the dataset's stringified lists into real Python lists.

In the Food.com dataset, columns like ``tags`` and ``ingredients`` are stored as
strings that look like Python lists, e.g. ``"['garlic', 'salt']"``. These helpers
convert them back safely.
"""

import ast


def parse_list(value) -> list:
    """Convert a stringified list into a real list of strings.

    Accepts values that are already lists, ``None``, or list-literal strings.
    Never raises: anything unparseable becomes an empty list.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value]

    text = str(value).strip()
    if not text:
        return []

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple)):
            return [str(item).strip() for item in parsed]
    except (ValueError, SyntaxError):
        pass

    # Fallback: treat a plain comma-separated string as a list.
    return [chunk.strip() for chunk in text.split(",") if chunk.strip()]


def parse_float_list(value) -> list:
    """Like :func:`parse_list` but keeps numeric values as floats."""
    numbers = []
    for item in parse_list(value):
        try:
            numbers.append(float(item))
        except (TypeError, ValueError):
            continue
    return numbers
