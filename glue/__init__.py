# file: __init__.py
# author: Vishesh Gupta
# created: 21 May 2016

__version__ = "0.1.0"

from glue.parser import parse
from glue.elements import Nesting, Block, Inline, block, inlineone
from glue.registry import Registry