from glue.parser import parse, parseinline, parseblock
from glue.elements import Block, Inline, Bold, Italic, Monospace, Paragraphs
from glue.registry import Registry

import inspect
import types

def unwind(g):
  l = []
  for e in g:
    if (isinstance(e, types.GeneratorType)
        or inspect.isgenerator(e)
        or inspect.isgeneratorfunction(e)):
      l.append(unwind(e))
    else:
      l.append(e)
  return l
  
sample = Registry(Bold, Italic, Monospace, Paragraphs)

def test_parseinline_empty():
  assert parseinline(sample, Paragraphs, '') == []

def test_parseinline_nosub():
  examples = ['test', ' ', 'a;lkjfksdfnqwenqw;eriouZN<ZMXz;lkj;sldakfjsf']
  for e in examples:
    assert parseinline(sample, Paragraphs, e) == [e]

def test_parseinline_basic():
  assert parseinline(sample, Paragraphs, '*text*') == [['strong', {}, 'text']]
  assert parseinline(sample, Paragraphs, '*`text`*') == [
    ['strong', {}, ['code', {}, 'text']]]

def test_parseblock_empty():
  assert unwind(parseblock(sample, Paragraphs, '')) == ['div', ['p']]

def test_parseblock_nosub():
  examples = ['test', 'k', 'a;lkjfksdfnqwenqw;eriouZN<ZMXz;lkj;sldakfjsf']
  for e in examples:
    assert unwind(parseblock(sample, Paragraphs, e)) == ['div', ['p', e]]
  
