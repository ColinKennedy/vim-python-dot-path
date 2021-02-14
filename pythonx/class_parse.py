#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import textwrap

try:
    _CANDIDATES = (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef)  # Python 3
except AttributeError:
    _CANDIDATES = (ast.FunctionDef, ast.ClassDef)  # Python 2


def _compute_interval(node):
    min_lineno = node.lineno
    max_lineno = node.lineno

    for node_ in ast.walk(node):
        if hasattr(node_, "lineno"):
            min_lineno = min(min_lineno, node_.lineno)
            max_lineno = max(max_lineno, node_.lineno)

    return (min_lineno, max_lineno + 1)


def _get_inner_dot_path(node):
    parent = node
    name = []

    while hasattr(parent, "parent"):
        name.append(parent.name)

        parent = parent.parent

    return ".".join(reversed(name))


def _get_line_dot_path(row, lines, column=0):
    parsed = ast.parse("\n".join(lines))
    size = len(lines)

    if row > size:
        raise ValueError(
            'Row "{row}" cannot be greater that line length, "{size}".'.format(
                row=row, size=size
            )
        )

    tree = text_to_tree(parsed, size)
    node = tree[row]

    if not column:
        return _get_inner_dot_path(node)

    node = _get_module_or_inner_scope(row, tree, column, node)

    return _get_inner_dot_path(node)


def _get_module_or_inner_scope(row, tree, column, fallback):
    test_row = row

    while test_row:
        test_row -= 1
        test_node = tree[test_row]

        if not hasattr(test_node, "col_offset"):
            continue

        if column - 4 >= test_node.col_offset:
            return test_node

        return fallback


def text_to_tree(parsed, module_end):
    tree = dict()

    for node in ast.walk(parsed):
        # 1. Add parent data to each node so that it can be queried, later
        for child in ast.iter_child_nodes(node):
            child.parent = node

        # 2. Add each node, per-line, to our tree
        if isinstance(node, ast.Module):
            tree.update(dict.fromkeys(range(module_end), node))
        elif isinstance(node, _CANDIDATES):
            start, end = _compute_interval(node)
            tree.update(dict.fromkeys(range(start, end), node))

    return tree


def main():
    """Run the main execution of the current script."""
    text = textwrap.dedent(
        """\
        class Foo(object):
            def method(self):
                pass

            class Inner(object):
                @classmethod
                def _thing(cls):
                    def _another_one():
                        pass

        """
    )
    lines = text.split("\n")
    row = 4
    column = 0 * 4  # 4 indentations * 4 spaces

    print(_get_line_dot_path(row, lines, column=column))


if __name__ == "__main__":
    main()
