#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module which traverses Python code and gets a dot-separated path to Python objects.

See Also:
    :func:`get_dot_path`.

"""

import ast

try:
    _CANDIDATES = (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef)  # Python 3
except AttributeError:
    _CANDIDATES = (ast.FunctionDef, ast.ClassDef)  # Python 2


def _compute_interval(node):
    """Get the start and end positions of some AST node.

    Args:
        node (:class:`ast.AST`): Some Python node to query from.

    Returns:
        tuple[int, int]:
            Two 0-based positions, indicating the row that the source
            code of `node` starts on and ends on.

    """
    minimum = node.lineno
    maximum = node.lineno

    for node_ in ast.walk(node):
        if hasattr(node_, "lineno"):
            minimum = min(minimum, node_.lineno)
            maximum = max(maximum, node_.lineno)

    return (minimum, maximum + 1)


def _get_indent(line):
    """str: Get the prefix whitespace characters from `line`."""
    return line[:len(line) - len(line.lstrip())]


def _get_inner_dot_path(node):
    """Get the Python dot-path for an AST node.

    This function assumes that the AST node has been optionally extended
    to have a parent node.

    See Also:
        :func:`_text_to_tree`.

    Args:
        node (:class:`ast.AST`):
            The AST node which we assume is a Python class / function /
            method definition.

    Returns:
        str: The found Python dot-separated path. e.g. "tests.test_foo.Class.get_blah".

    """
    parent = node
    name = []

    while hasattr(parent, "parent"):
        name.append(parent.name)

        parent = parent.parent

    return ".".join(reversed(name))


def _get_node_or_parent(row, tree, column):
    """Check if `fallback` should be returned or a parent node in the `tree`.

    Args:
        row (int):
            A 0-based index value for the user's cursor position.
        tree (list[:class:`ast.AST`]):
            A parsed tree of Python class / function / method definitions.
        column (int):
            A 0-based index value for the user's cursor offset.

    Returns:
        :class:`ast.AST`: Either `fallback` or another node within `tree`.

    """
    fallback = tree[row]
    test_node = tree[row - 1]

    if hasattr(fallback, "col_offset") and column >= fallback.col_offset:
        return fallback

    if hasattr(test_node, "col_offset") and column >= test_node.col_offset:
        return test_node

    return fallback


def _text_to_tree(graph, line_count):
    """Get every class / function / method from a AST Python module.

    Args:
        graph (:class:`ast.Module`): Some Python module to parse.
        line_count (int): The total lines in the file.

    Raises:
        ValueError: If `line_count` is less than 0.

    Returns:
        list[:class:`ast.AST`]:
            Each node found on each line. If the line does not define a
            class, function, or method, `graph` is used instead.

    """
    if line_count < 0:
        raise ValueError(
            'Line count "{line_count}" cannot be less than zero.'.format(
                line_count=line_count
            )
        )

    tree = [graph for _ in range(line_count)]

    for node in ast.walk(graph):
        # 1. Add parent data to each node so that it can be queried, later
        for child in ast.iter_child_nodes(node):
            child.parent = node

        # 2. Add each node, per-line, to our tree
        if isinstance(node, ast.Module):
            continue
        elif isinstance(node, _CANDIDATES):
            start, end = _compute_interval(node)

            for value in range(start - 1, end - 1):
                tree[value] = node

    return tree


def get_dot_path(row, lines, column=0):
    """Get the Python dot-path for the user's requested cursor position.

    Args:
        row (int):
            A 0-based index value for the user's cursor position.
        lines (container[str]):
            Every Python source code line which will be parsed for a dot path.
        column (int, optional):
            A 0-based index value for the user's cursor offset.

    Raises:
        ValueError: If `row` is to big and exceeds the length of `lines`.

    Returns:
        str: The found Python dot-separated path. e.g. "tests.test_foo.Class.get_blah".

    """
    size = len(lines)

    if row > size:
        raise ValueError(
            'Row "{row}" cannot be greater that line length, "{size}".'.format(
                row=row, size=size
            )
        )

    try:
        graph = ast.parse("\n".join(lines))
    except IndentationError:
        # If the user is still typing a line, just add fake text so we can still process it.
        previous_line = lines[-2]
        prefix = _get_indent(previous_line)
        lines.append("{prefix}    pass".format(prefix=prefix))
        size += 1
        graph = ast.parse("\n".join(lines))

    tree = _text_to_tree(graph, size)
    node = tree[row]

    if not column:
        return _get_inner_dot_path(node)

    node = _get_node_or_parent(row, tree, column)

    return _get_inner_dot_path(node)
