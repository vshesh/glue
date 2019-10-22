import pytest

from glue import parse
from glue.library import *
from glue.util import unwind

from hypothesis import given
from hypothesis.strategies import text, integers

import string


@given(text(alphabet=(string.digits+string.whitespace+string.ascii_letters)))
def test_singlegroups(s: str):
  assert unwind(parse(Registry(NoopBlock, Bold), '*'+s+'*', NoopBlock)) == ['div', ['strong', {}, s]]
  assert unwind(parse(Registry(NoopBlock, Italic), '_'+s+'_', NoopBlock)) == ['div', ['em', {}, s]]
  assert unwind(parse(Registry(NoopBlock, Monospace), '`'+s+'`', NoopBlock)) == ['div', ['code', {}, s]]


def test_tooltip():
  assert unwind(
    parse(Registry(NoopBlock, Tooltip), 'T[text](tooltip)', NoopBlock)) == [
           'div', ['span.tooltip', 'text', ['div.tooltip-text', 'tooltip']]]


@given(text(alphabet=(string.digits+string.ascii_letters)), integers(min_value=1, max_value=6))
def test_header(s: str, n: int):
  assert unwind(parse(Registry(Paragraphs, Header), '#'*n+' '+s, Paragraphs)) == [
    'div', ['h'+str(n), ['a', {'name': s.lower()}, s]]]


def test_criticsub():
  assert unwind(parse(Registry(Paragraphs, CriticSub), '{~~a~>b~~}', Paragraphs)) == [
    'div', ['p', [['del', 'a'], ['ins', 'b']]]]


def test_sidebyside():
  assert list(SideBySide('c | x')) == ['div', {'style': {'display': 'flex'}},
                                       ['div', {'style': {'flex': '1'}}, 'c'],
                                       ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c|x')) == ['div', {'style': {'display': 'flex'}},
                                     ['div', {'style': {'flex': '1'}}, 'c'],
                                     ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c |x')) == ['div', {'style': {'display': 'flex'}},
                                      ['div', {'style': {'flex': '1'}}, 'c'],
                                      ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c| x')) == ['div', {'style': {'display': 'flex'}},
                                      ['div', {'style': {'flex': '1'}}, 'c'],
                                      ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c \| x')) == ['div', {'style': {'display': 'flex'}},
                                        ['div', {'style': {'flex': '1'}},
                                         'c \\| x']]
  assert list(SideBySide('a|b|c\nd|e')) == ['div',
                                            {'style': {'display': 'flex'}},
                                            ['div', {'style': {'flex': '1'}},
                                             'a\nd'],
                                            ['div', {'style': {'flex': '1'}},
                                             'b\ne'],
                                            ['div', {'style': {'flex': '1'}},
                                             'c\n']]
  assert list(SideBySide('a')) == ['div', {'style': {'display': 'flex'}},
                                   ['div', {'style': {'flex': '1'}}, 'a']]

def test_matrix():
  assert unwind(Matrix('c | x')) == ['div.matrix.matrix-flex',
                                     ['div', {'style': {'display': 'flex'}},
                                      ['span', {'style': {'flex': 1}}, 'c'],
                                      ['span', {'style': {'flex': 1}}, 'x']]]

  assert unwind(Matrix('c|x')) == ['div.matrix.matrix-flex',
                                     ['div', {'style': {'display': 'flex'}},
                                      ['span', {'style': {'flex': 1}}, 'c'],
                                      ['span', {'style': {'flex': 1}}, 'x']]]

  assert unwind(Matrix('c| x')) == ['div.matrix.matrix-flex',
                                     ['div', {'style': {'display': 'flex'}},
                                      ['span', {'style': {'flex': 1}}, 'c'],
                                      ['span', {'style': {'flex': 1}}, 'x']]]

  assert unwind(Matrix('c |x')) == ['div.matrix.matrix-flex',
                                     ['div', {'style': {'display': 'flex'}},
                                      ['span', {'style': {'flex': 1}}, 'c'],
                                      ['span', {'style': {'flex': 1}}, 'x']]]

  assert unwind(Matrix('c | x', type='matrix')) == [
    'table.matrix.matrix-table',
    ['tr', {'style': {}},
     ['td', {}, 'c'],
     ['td', {}, 'x']]]

def test_list():
  s = '''
  one
  two
  three
  '''
  assert List(s) == ['ul', ['li', 'one'], ['li', 'two'], ['li', 'three']]
  s2 = '''
  one
   sub one
   sub two
     sub sub one
  two
   two sub one
  '''
  assert List(s2) == ['ul', ['li', 'one', ['ul', ['li', 'sub one'], ['li', 'sub two', ['ul', ['li', 'sub sub one']]]]],
                      ['li', 'two', ['ul', ['li', 'two sub one']]]]


def test_annotated_code():
  s = '''
#comment 1
def f1(x):
  return x
'''
  assert AnnotatedCode(s) == ['AnnotatedCode', {'code': '\ndef f1(x):\n  return x',
                                                'annotations': {1:'comment 1\n'},
                                                'language': 'python'}]

@given(text())
def test_noop(s: str):
  assert list(NoopBlock(s)) == ['div', s]


def test_standard_registry():
  t1="""
# Placeholder

* bold *

new paragraph
  """
  assert unwind(parse(Standard, t1)) == ['div', ['h1', ['a', {'name': 'placeholder'}, 'Placeholder']],
                                                ['p', ['strong', {}, ' bold ']],
                                                ['p', 'new paragraph']]

listtestsimple = '''
A
B
  a
  b
    c
D
  e
G
'''

listtest = '''
Grading Notes    1
Introduction    2
  “Model Cell”    3
  What we know    4
  What we don’t know    4
Methods    5
  Criteria for Selection    5
  Research Site    5
  Data Sources    6
  Analysis    7
Findings    7
  County Hospital is invested in “learning”    7
    Prior Efforts    8
    Evolution of process    8
    Support from leadership    9
  A critical tension exists between learning and “getting a win”    10
    LEAN consultants perceive their function as “developing capacity for scientific problem solving”    11
    Participants apply to the model cell because of their desire to learn    12
    Many stakeholders want the project to be completed successfully    13
  LEAN Facilitators resolve this conflict    16
    “Timely learning” is LEAN’s design for development within a model cell    16
    LEAN Facilitators must map the situation at hand to a tool or process    17
    Delineated “teaching moments”    18
    Interventions resolve team conflicts for the LEAN Facilitators and the participants    19
  End state: everyone’s a scientist, but teamwork is still hard!    20
    Adopting the improvement mindset    20
    The “next stage of excellence”    21
    Ideal state    21
Discussion    22
  Contribution to group learning literature    22
  Future Work    22
Works Cited    23
'''
def test_list():
  assert List(listtestsimple) == []
