
from glue import parse
from glue.library import *
from glue.util import unwind

def test_tooltip():
  assert unwind(parse(Registry(NoopBlock, Tooltip), 'T[text](tooltip)', NoopBlock)) == ['div', ['span.tooltip', 'text', ['div.tooltip-text', 'tooltip']]]

def test_header():
  assert unwind(parse(Registry(Paragraphs, Header), '# h1', Paragraphs)) == ['div', ['h1', ' h1']]
  assert unwind(parse(Registry(Paragraphs, Header), '# h1\n## h2\n### h3', Paragraphs)) == ['div', ['h1', ' h1'], ['h2', ' h2'], ['h3', ' h3']]

def test_sidebyside():
  assert list(SideBySide('c | x')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'c'], ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c|x')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'c'], ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c |x')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'c'], ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c| x')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'c'], ['div', {'style': {'flex': '1'}}, 'x']]
  assert list(SideBySide('c \| x')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'c \\| x']]
  assert list(SideBySide('a|b|c\nd|e')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'a\nd'], ['div', {'style': {'flex': '1'}}, 'b\ne'], ['div', {'style': {'flex': '1'}}, 'c\n']]
  assert list(SideBySide('a')) == ['div', {'style': {'display': 'flex'}}, ['div', {'style': {'flex': '1'}}, 'a']]

def test_noop():
  assert list(NoopBlock('text')) == ['div', 'text']
  assert list(NoopBlock('text\n\nmore text')) == ['div', 'text\n\nmore text']