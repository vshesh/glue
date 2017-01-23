import pytest

from glue import parse
from glue.library import *
from glue.util import unwind


@pytest.mark.randomize(str_attrs=('digits', 'whitespace', 'ascii_letters'))
def test_singlegroups(s: str):
  assert unwind(parse(Registry(NoopBlock, Bold), '*'+s+'*', NoopBlock)) == ['div', ['strong', {}, s]]
  assert unwind(parse(Registry(NoopBlock, Italic), '_'+s+'_', NoopBlock)) == ['div', ['em', {}, s]]
  assert unwind(parse(Registry(NoopBlock, Monospace), '`'+s+'`', NoopBlock)) == ['div', ['code', {}, s]]

def test_tooltip():
  assert unwind(
    parse(Registry(NoopBlock, Tooltip), 'T[text](tooltip)', NoopBlock)) == [
           'div', ['span.tooltip', 'text', ['div.tooltip-text', 'tooltip']]]

@pytest.mark.randomize(str_attrs=('digits', 'ascii_letters'), min_num=1, max_num=6)
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
  '''
  assert List(s2) == ['ul', ['li', 'one', ['ul', ['li', 'sub one'], ['li', 'sub two', ['ul', ['li', 'sub sub one']]]]],
                      ['li', 'two']]


@pytest.mark.randomize()
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
