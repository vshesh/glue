from glue import *
from glue.parser import parseinline, parseblock
from glue.library import Bold, Italic, Monospace, Link, Paragraphs
from glue.util import unwind

sample = Registry(Bold, Italic, Monospace, Paragraphs)

# --------------------------------- PARSEINLINE TESTS --------------------

def test_parseinline_empty():
  assert parseinline(sample, Paragraphs, '') == []


def test_parseinline_nosub():
  examples = ['test', ' ', 'a;lkjfksdfnqwenqw;eriouZN<ZMXz;lkj;sldakfjsf']
  for e in examples:
    assert parseinline(sample, Paragraphs, e) == [e]


def test_parseinline_basic():
  assert parseinline(sample, Paragraphs, '*text*') == [(Bold, ['strong', {}, 'text'])]
  assert parseinline(sample, Paragraphs, '*`text`*') == [
    (Bold, ['strong', {}, (Monospace, ['code', {}, 'text'])])]
  assert parseinline(sample, Paragraphs, '*text**text2*') == [
    (Bold, ['strong', {}, 'text']),
    (Bold, ['strong', {}, 'text2'])]


def test_parseinline_multiline():
  assert parseinline(sample, Paragraphs, '*te\nxt*') == [(Bold, ['strong', {}, 'te\nxt'])]

def test_parseinline_post():
  assert parseinline(sample + [Link], Paragraphs,
                     '[link](http://google.com)') == [(Link, ['a', {'href': 'http://google.com'}, 'link'])]
  assert parseinline(sample + [Link], Paragraphs,
                     '[*link*](http://google.com)') == [(Link, ['a', {'href': 'http://google.com'}, (Bold, ['strong', {}, 'link'])])]


def test_parseinline_none():
  @inlineone(r'\@([^@]+)\@', nest=Nesting.NONE, subinline=[])
  def InlineNone(groups):
    return ['p', groups[0]]

  assert parseinline(sample + [InlineNone], Paragraphs,
                     '@*bold* _italic_ abc@') == [(InlineNone, ['p', '*bold* _italic_ abc'])]


def test_parseinline_embedded():
  assert parseinline(sample, Paragraphs, 'text *bold* text') == ['text ', (Bold, ['strong', {}, 'bold']), ' text']


# ------------------ PARSEBLOCK TESTS ----------------------------------------

def test_parseblock_empty():
  assert unwind(parseblock(sample, Paragraphs, '')) == ['div']


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


@block(nest=Nesting.SUB)
def IdentityBlock(text):
  return ['div', text]

def test_parseblock_nestingsub():
  # should consume paragraphs block
  assert unwind(parseblock(Registry(IdentityBlock, Paragraphs), IdentityBlock,
                    'hello\n---paragraphs\nhello\n...\n')) == ['div', 'hello\n', ['div', ['p', 'hello']]]

def test_parseblock_nestingsub_multiple():
  assert unwind(parseblock(sample + [IdentityBlock], IdentityBlock,
                           '*hello*\n---paragraphs\nhello\n---paragraphs\nhello again\n...\n...\n')) == ['div', ['strong', {}, 'hello'], '\n', ['div', ['p', 'hello'], ['div', ['p', 'hello again']]]]

  assert unwind(parseblock(sample, Paragraphs,
                           ' *hello*\n---paragraphs\nhello\n---paragraphs\n*hello* again\n...\n...\n')) == [
           'div', ['p', ' ', ['strong', {}, 'hello']],
           ['div', ['p', 'hello'], ['div', ['p', ['strong', {}, 'hello'], ' again']]]]


def test_parseblock_nestingpost():
  @block()
  def IdentityBlock(text):
    return ['div', text]

  assert unwind(parseblock(Registry(IdentityBlock, Paragraphs), IdentityBlock,
                           'hello\n---paragraphs\nhello\n...\n')) == ['div', 'hello\n', ['div', ['p', 'hello']]]



















