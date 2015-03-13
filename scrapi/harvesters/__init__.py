"""Importing harvesters imports all file and folders contained in
the harvesters folder. All harvesters should be defined in here.
NOTE: Empty folders in will cause this to break
"""
import os

# Get a list of folders
_, __all__, files = next(os.walk(os.path.dirname(__file__)))

for name in files:
    # Find all .py files that are not init
    if name[-3:] == '.py' and name != '__init__.py':
        __all__.append(name[:-3])

# Import everything in __all__
from . import *
