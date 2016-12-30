
from glue import parse
from glue.library import *
from glue.util import unwind

def test_bold():
  assert unwind(parse(Registry(NoopBlock, Bold), '*bold*', NoopBlock)) == ['div', ['strong', {}, 'bold']]

def test_tooltip():
  assert unwind(parse(Registry(NoopBlock, Tooltip), 'T[text](tooltip)', NoopBlock)) == ['div', ['span.tooltip', 'text', ['div.tooltip-text', 'tooltip']]]

def test_header():
  assert unwind(parse(Registry(Paragraphs, Header), '# h1', Paragraphs)) == ['div', ['h1', 'h1']]
  assert unwind(parse(Registry(Paragraphs, Header), '# h1\n## h2\n### h3', Paragraphs)) == ['div', ['h1', 'h1'], ['h2', 'h2'], ['h3', 'h3']]

def test_criticsub():
  assert unwind(parse(Registry(Paragraphs, CriticSub), '{~~a~>b~~}', Paragraphs)) == ['div', ['p', [['del', 'a'], ['ins', 'b']]]]

def test_sidebyside():
  assert list(SideBySide('c | x')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'c'], ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c|x')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'c'], ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c |x')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'c'], ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c| x')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'c'], ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c \| x')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'c \\| x']]
  assert list(SideBySide('a|b|c\nd|e')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'a\nd'], ['div', {'style': {'flex': '1'}}, 'b\ne'], ['div', {'style': {'flex': '1'}}, 'c\n']]
  assert list(SideBySide('a')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'a']]

def test_matrix():
  assert unwind(Matrix('c | x')) == ['div', {'class': 'matrix matrix-flex'},
                                     ['div', {'style': {'display': 'flex'}},
                                      ['span', {'flex': 1}, 'c'],
                                      ['span', {'flex': 1}, 'x']]]

  assert unwind(Matrix('c|x')) == ['div', {'class': 'matrix matrix-flex'},
                                     ['div', {'style': {'display': 'flex'}},
                                      ['span', {'flex': 1}, 'c'],
                                      ['span', {'flex': 1}, 'x']]]

  assert unwind(Matrix('c| x')) == ['div', {'class': 'matrix matrix-flex'},
                                     ['div', {'style': {'display': 'flex'}},
                                      ['span', {'flex': 1}, 'c'],
                                      ['span', {'flex': 1}, 'x']]]

  assert unwind(Matrix('c |x')) == ['div', {'class': 'matrix matrix-flex'},
                                     ['div', {'style': {'display': 'flex'}},
                                      ['span', {'flex': 1}, 'c'],
                                      ['span', {'flex': 1}, 'x']]]

  assert unwind(Matrix('c | x', type='matrix')) == ['table', {'class': 'matrix matrix-table'},
                                     ['tr', {'style': {}},
                                      ['td', {}, 'c'],
                                      ['td', {}, 'x']]]


def test_noop():
  assert list(NoopBlock('text')) == ['div', 'text']
  assert list(NoopBlock('text\n\nmore text')) == ['div', 'text\n\nmore text']

def test_standard_registry():
  t1="""
# Placeholder

* bold *

new paragraph
  """
  assert unwind(parse(Standard, t1)) == ['div', ['h1', 'Placeholder'],
                                                ['p', ['strong', {}, ' bold ']],
                                                ['p', 'new paragraph']]
