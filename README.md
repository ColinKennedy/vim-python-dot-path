# vim-python-dot-finder
A simple Python mapping for querying the dot-separated paths from the user's cursor.

```python
class SomeClass(object):
    def get_thing(self):
        # ...
        stuff  # <-- cursor located here
        # ...
```

Just call this function:

```vim
:echo GetCurrentDotPath()
```

And it will return "SomeClass.get_thing".


## About Packaging
This Vim plugin was built specifically to work with Rez packages. If the
Vim function is run within a Rez package, you'll get the full Python
import, up until wherever you've placed the Rez package.py file.


## Running Tests
Run this

```sh
PYTHONPATH=$PWD/pythonx python -m unittest discover
```

And all tests should pass.
