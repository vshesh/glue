from glue import *
from glue.parser import parseinline, parseblock
from glue.library import Bold, Italic, Monospace, Link, Paragraphs
from glue.util import unwind

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
  assert parseinline(sample, Paragraphs, '*text**text2*') == [
    ['strong', {}, 'text'],['strong', {}, 'text2']]


def test_parseinline_post():
  assert parseinline(sample + [Link], Paragraphs,
                     '[link](http://google.com)') == [['a', {'href': 'http://google.com'}, 'link']]
  assert parseinline(sample + [Link], Paragraphs,
                     '[*link*](http://google.com)') == [['a', {'href': 'http://google.com'}, ['strong', {}, 'link']]]


def test_parseinline_none():
  @inlineone(r'\@([^@]+)\@', nest=Nesting.NONE, subinline=[])
  def InlineNone(groups):
    return ['p', groups[0]]

  assert parseinline(sample + [InlineNone], Paragraphs,
                     '@*bold* _italic_ abc@') == [['p', '*bold* _italic_ abc']]


def test_parseblock_empty():
  assert unwind(parseblock(sample, Paragraphs, '')) == ['div', ['p']]


def test_parseblock_nosub():
  examples = ['test', 'k', 'a;lkjfksdfnqwenqw;eriouZN<ZMXz;lkj;sldakfjsf']
  for e in examples:
    assert unwind(parseblock(sample, Paragraphs, e)) == ['div', ['p', e]]


def test_parseblock_nestingnone():
  @block(nest=Nesting.NONE)
  def IdentityBlock(text):
    return ['p', text]

  # should not consume another block
  assert parseblock(Registry(IdentityBlock, Paragraphs), IdentityBlock,
                    '---paragraphs\n...\n') == ['p', '---paragraphs\n...\n']


def test_parseblock_nestingsub():
  @block(nest=Nesting.SUB)
  def IdentityBlock(text):
    return ['p', text]

  # should consume paragraphs block
  assert unwind(parseblock(Registry(IdentityBlock, Paragraphs), IdentityBlock,
                    'hello\n---paragraphs\nhello\n...\n')) == ['p', 'hello\n', ['div', ['p', 'hello']]]
