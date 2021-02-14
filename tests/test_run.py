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
        self.assertEqual(
            "_foo",
            _get_dot_path(
                """\

                def _foo(
                    asdfasdf,
                    ttttttt,
                    blah=None,
                    another=1111111,
                ):
                    |x|
                    pass
                """
            )
        )

    def test_method(self):
        """Get the dot-separated path from a method of a class."""
        self.assertEqual(
            "SomeClass._staticy",
            _get_dot_path(
                """\

                class SomeClass(object):
                    @staticmethod
                    def _staticy():
                        pass |x|
                """
            )
        )

    def test_permutations(self):
        classes = [
            '''\
            class SomeClass(object):
                """Single-line |x|docstring."""
            ''',
            '''\
            class SomeClass(object):
                """Single-line docstring."""|x|
            ''',
            '''\
            class SomeClass(object):
                "|x|""Single-line docstring."""
            ''',
            '''\
            class SomeClass(object):

                |x|"""Single-line docstring."""

            ''',
            '''\
            class SomeClass(object):

                |x|

                """Single-line docstring."""

            ''',
            '''\
            class SomeClass(
                object,
                    WeirdIndentation, |x|
            ):
                """Single-line docstring."""

            ''',
            '''\
            class |x|SomeClass(object):
                """Single-line docstring."""

            ''',
            '''\
            class SomeClass(ob|x|ject):
                """Single-line docstring."""

            ''',
            '''\
            c|x|lass SomeClass(object):
                """Single-line docstring."""

            ''',
            '''\
            class SomeClass(object):

                |x|"""A multi-line docstring.

                It spans several lines and is long!

                """

            ''',
            '''\
            class SomeClass(object):

                """A multi-line docstring.

                It span|x|s several lines and is long!

                """

            ''',
            '''\
            class SomeClass(object):
                |x|

                """A multi-line docstring.

                It spans several lines and is long!

                """
            ''',
            '''\
            class SomeClass(object):
                """A multi-line docstring.

                It spans several lines and is long!

                """
                |x|
            ''',
            '''\
            class SomeClass(object):
                """A multi-line docstring.

                It spans several lines and is long!

                """|x|
            ''',
        ]

        permutations = []
        permutations.extend((text, "SomeClass") for text in classes)
        # permutations.extend((text, "SomeClass.get_method") for text in methods)
        # permutations.extend((text, "do_function") for text in functions)

        for text, expected in permutations:
            self.assertEqual(expected, _get_dot_path(text), msg=text)


def _get_dot_path(text):
    text = textwrap.dedent(text)
    lines = text.split("\n")
    row = -1
    column = -1

    for row, line in enumerate(lines):
        try:
            column = line.index(_CURSOR)
        except ValueError:
            pass
        else:
            break
    else:
        raise RuntimeError('Cursor "{_CURSOR}" was not found.'.format(_CURSOR=_CURSOR))

    if row == -1:
        raise RuntimeError('No row was found.')

    if column == -1:
        raise RuntimeError('No column was found.')

    text = text.replace(_CURSOR, "")

    return dot_finder.get_dot_path(row, text.split("\n"), column=column)
