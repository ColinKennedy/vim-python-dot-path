#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure :mod:`dot_finder` works as expected."""

import unittest
import textwrap

import dot_finder

_CURSOR = "|x|"


class Run(unittest.TestCase):
    """Make sure :func:`dot_finder.get_dot_path` works as expected."""

    def test_class(self):
        """Get the dot-separated path from a class."""
        self.assertEqual(
            "SomeClass",
            _get_dot_path(
                """\

                class SomeClass(object):
                    |x|
                    pass
                """
            )
        )

    def test_function(self):
        """Get the dot-separated path from a function."""
        raise ValueError()

    def test_method(self):
        """Get the dot-separated path from a method of a class."""
        raise ValueError()

    def test_permutations(self):
        raise ValueError()


def _get_dot_path(text):
    text = textwrap.dedent(text)
    row = -1
    column = -1

    for row, line in enumerate(text):
        try:
            column = line.index(_CURSOR)
        except ValueError:
            break
    else:
        raise RuntimeError('Cursor "{_CURSOR}" was not found.'.format(_CURSOR=_CURSOR))

    if row == -1:
        raise RuntimeError('No row was found.')

    if column == -1:
        raise RuntimeError('No column was found.')

    text = text.replace(_CURSOR, "")

    return dot_finder.get_dot_path(row, text.split("\n"), column=column)
