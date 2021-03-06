import pytest

from glue.parser import *
from glue.library import Bold, Italic, Monospace, Link, Paragraphs, Standard, block, inline
from glue.util import unwind

sample = Registry(Bold, Italic, Monospace, Paragraphs)

from hypothesis import given
from hypothesis.strategies import text, integers
import string

# --------------------------------- PARSEINLINE TESTS --------------------

words = text(alphabet=(string.ascii_letters+string.digits+string.whitespace))

def test_parseinline_empty():
  assert parseinline(sample, Paragraphs, '') == ['']
  assert parseinline(Standard, Paragraphs, '**') == [(Bold, ['strong', {}, ''])]
  assert unwind(parse(Standard, '')) == ['div']
  

@given(words)
def test_parseinline_nosub(s: str):
  assert parseinline(sample, Paragraphs, s) == [s]


def test_parseinline_basic():
  assert parseinline(sample, Paragraphs, '*text*') == [(Bold, ['strong', {}, 'text'])]
  assert parseinline(sample, Paragraphs, '*`text`*') == [
    (Bold, ['strong', {}, (Monospace, ['code', {}, 'text'])])]
  assert parseinline(sample, Paragraphs, '*text**text2*') == [
    (Bold, ['strong', {}, 'text']),
    (Bold, ['strong', {}, 'text2'])]


@given(words, words)
def test_parseinline_multiline(s1: str, s2: str):
  assert parseinline(sample, Paragraphs, '*{}\n{}*'.format(s1, s2)) == [(Bold, ['strong', {}, s1 + '\n' + s2])]

def test_parseinline_post():
  assert parseinline(sample + [Link], Paragraphs,
                     '[link](http://google.com)') == [(Link, ['a', {'href': 'http://google.com', 'target': '_blank'}, 'link'])]
  assert parseinline(sample + [Link], Paragraphs,
                     '[*link*](http://google.com)') == [(Link, ['a', {'href': 'http://google.com', 'target': '_blank'}, (Bold, ['strong', {}, 'link'])])]


def test_parseinline_none():
  @inline(r'\@([^@]+)\@', nest=Nesting.NONE, sub=[])
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
                           '*hello*\n---paragraphs\nhello\n---paragraphs\nhello again\n...\n...\n')) == [
           'div', ['strong', {}, 'hello'], '\n', ['div', ['p', 'hello'], ['div', ['p', 'hello again']]]]

  assert unwind(parseblock(sample, Paragraphs,
                           ' *hello*\n---paragraphs\nhello\n---paragraphs\n*hello* again\n...\n...\n')) == [
           'div', ['p', ' ', ['strong', {}, 'hello']],
           ['div', ['p', 'hello'], ['div', ['p', ['strong', {}, 'hello'], ' again']]]]


def test_parseblock_nestingpost():
  assert unwind(parseblock(Registry(IdentityBlock, Paragraphs), IdentityBlock,
                           'hello\n---paragraphs\nhello\n...\n')) == ['div', 'hello\n', ['div', ['p', 'hello']]]

# -------------- PARSE Inline Inside a Inline element with display: block

def test_parse_header():
  assert unwind(parse(Standard, '# Header ![img](imgurl)')) == [
    'div', ['h1', ['a.anchor', {'id': 'header-imgimgurl'},
                   'Header ', ['img.full-image', {'alt': 'img', 'src': 'imgurl',
    'style': {'margin': '0 auto', 'display': 'block', 'max-width': '100%'}}]]]]
  assert unwind(
    parse(Standard, '# h1\n## h2\n### h3', Paragraphs)) == [
           'div', ['h1', ['a.anchor', {'id': 'h1'}, 'h1']],
                  ['h2', ['a.anchor', {'id': 'h2'}, 'h2']],
                  ['h3', ['a.anchor', {'id': 'h3'}, 'h3']]]


@given(words)
def test_regex_clash(s: str):
  assert unwind(parse(Standard, '__'+s+'__')) == [
    'div', ['p', ['span', {'style': 'text-decoration:underline;'}, s]]]


# ------------- MACROExpand test

@given(words)
def test_macroexpand(s: str):
  assert macroexpand({'x': 'x'}, s) == s
  assert macroexpand({'x': 'x'}, '${x} ' + s) == 'x ' + s
  assert macroexpand({'x': 'x'}, s + ' ${x}') == s + ' x'
  assert macroexpand({'x': 'x ${y}', 'y': 'y'}, '${x} ' + s) == 'x y ' + s


@given(text(alphabet=(string.ascii_letters+string.digits)), text(alphabet=(string.ascii_letters+string.digits)))
def test_parsemacros(name: str, text: str):
  assert unwind(parsemacros('{} = {}'.format(name, text))) == [[name.strip(), text.strip()]]
