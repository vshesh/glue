import pytest
from hypothesis import given
from hypothesis.strategies import text, integers
import string

from glue.util import unwind
from glue.codegen import *

def test_render_imba_attrs_empty():
  assert render_imba_attrs({}) == ''

@given(text())
def test_render_imba_attrs_single(o):
  assert render_imba_attrs({o:1}) == f'{o}=1'

@given(text(alphabet='abcdefghijk_!@#$', min_size=1), 
       text(alphabet='lmnopqrstuvwxyz-?', min_size=1))
def test_render_imba_attrs_double(t, t2):
  assert render_imba_attrs({t:1, t2:2}) == f'{t}=1 {t2}=2'

def test_render_imba_attrs_