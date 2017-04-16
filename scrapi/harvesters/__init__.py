"""Importing harvesters imports all file and folders contained in
the harvesters folder. All harvesters should be defined in here.
NOTE: Empty folders in will cause this to break
"""
import os

dirname = os.path.dirname(__file__)


def files(dir):
    return next(os.walk(dir))[2]


def folders(dir):
    return map(lambda x: os.path.join(dir, x), next(os.walk(os.path.dirname(dir)))[1])

imports = map(files, folders('scrapi/harvesters/')) #TODO
# Get a list of folders
_, __all__, files = next(os.walk(dirname))

# remove __pycache__ directories
__all__ = [d for d in __all__ if d != '__pycache__']

# Find all .py files that are not init
__all__.extend([
    name[:-3]
    for name in files + imports
    if name[-3:] == '.py'
    and '__init__.py' not in name
])

# Import everything in __all__
from . import *
