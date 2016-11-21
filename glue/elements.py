#/usr/bin/env python3
import enum
from collections import namedtuple as nt
from enum import Enum
from typing import Mapping, Union, Set, Callable

import inflection
import regex as re

"""
FRAME nesting means that the block is intended to contain/frame the inside
text, which should be parsed using the parent of this block
POST means that the subtext in this block should be parsed AFTER this block is
parsed. This is the default, and is suitable for most situations
SUB means that the inside of the text is parsed for child nodes (inline and
block) first, and the corresponding sections are replaced with [|*|] style tags
that are meant to be left UNTOUCHED. After this block is parsed, then the tags
are replaced with the appropriate parsed sections
NONE means that this is a terminal block. Whatever is returned here will be
directly put into the result, without any sub processing.
"""
Nesting = Enum('Nesting', 'FRAME POST SUB NONE')
Display = Enum('Display', 'BLOCK INLINE')
# ------------------  BASE ELEMENTS --------------------------

class Block(nt('Block', ['name', 'nest', 'subblock', 'subinline', 'parser', 'opts'])):
  """
  Base class for elements that are enclosed in yaml-like document blocks.
  A block element is an element that is expected to render in the style of an
  html `div` element, and is represented in the plain-text format as:

  ```yaml
  ---block ...args
  text that will be parsed by the block goes here.
  ...
  ```

  The name of the block is put right after the `---` and is used to dispatch
  to the block with the appropriate name. The name of the block should be
  dasherized for style purposes (so that it's easier to type than capitals, and
  so that there's a consistent look).

  `nest` is the nesting policies for nesting blocks and inline elements.

  `subblock` is an array of names or literal block elements that this block
  accepts as sub-blocks. In general, most blocks will either be `Nesting.NONE` or
  accept every block, but you can be more specific if you'd like.

  `subinline` is the same for inline elements.

  `parser` is a function that takes string text and outputs html corresponding
  to whatever this block would like to parse.

  `opts` is a string passed to getopts that states which flags are allowed
  as kwargs options for this block.
  """
  def __new__(cls, name, nest=Nesting.POST, subblock=None, subinline=None, parser=None, opts=''):
    return super(Block, cls).__new__(cls,
      name,
      nest,
      subblock or ['all'],
      subinline or ['all'],
      parser or (lambda text: ['div', text]),
      opts)

  def __call__(self, *args, **kwargs):
    return self.parser(*args, **kwargs)

  def __hash__(self):
    return self.name.__hash__()


Inline = nt('Inline', ['name', 'display', 'nest', 'subinline', 'escape', 'parser'])
Inline.__hash__ = lambda self: self.name.__hash__()
Inline.__doc__ = """
Base class for elements that are meant to be inline in the text inside blocks.
An inline element is expected to render in the style of an html `span` element.

The representation of an inline element in plaintext is defined by the parser
object, which is designed differently than the parser element of a block.
The parser in an Inline element looks like a list of pairs, where the first
element in a pair is a regex and the second is a function that takes the
recorded groups of the regex and returns an html element, in cottonmouth form.

It's recommended to use the more advanced `regex` 2016 library that comes from
pip so that you can properly create regexes that allow escaped characters.

Eg, matching bold text might seem easy (`\*(.*?)\*`) but it is actually quite
complicated to ignore a literal `\*` in the text.
For very basic things, both helper methods and standard elements have been
provided so you don't have to write them yourself!

`nest` defines what nesting style the parser is expecting. `FRAME` is the most
common, and basically "passes through" parsing from the parent block element.
However, you can also define `POST` or `SUB` if you expect to do some of
your own parsing (eg, link elements work well with the `POST` style).

`subinline` is a list of either strings or literal element objects that define
which styles are allowed inside this style. The two special values are 'inherit'
and 'all'. 'inherit' is a dynamic key, and at parse-time the text inside the
element will be parsed as if it was in the enclosing block's scope. 'all' means
you would like to subscribe to ALL the inline styles in your registry. This is
a static key.

`escape` is a string or set containing characters that need to be escaped in the
block. eg, if you define syntax like `*bold*` to mean bold, then you would like
for the `*` character to be escapable so that the user can enter an actual
asterisk if they wish. Setting escape = "*" will tell the parser to translate
every `\*` sequence to a literal `*`. Every time you give a character a special
meaning, you have to make an escape sequence that allows you to enter the
character literally. This is most critical for the 1-char elements, but it's
important for others as well.
"""

# --------------------- ELEMENT UTILITIES ---------------------------------

def makename(name):
  """Turns a capital camelcase name into a dasherized name for block detection.
  Convenience function for blocks, mostly.
  """
  return inflection.dasherize(inflection.underscore(name))

@enum.unique
class Patterns(Enum):
  escape = '(?<!\\\\)(?:\\\\\\\\)*{0}'
  single_group = '(?<!\\\\)(?:\\\\\\\\)*\\K{0}(.+?(?<!\\\\)(?:\\\\\\\\)*){1}'
  link = r'(?<!\\)(?:\\\\)*\K{0}\[(.*?(?<!\\)(?:\\\\)*)\]\((.*?(?<!\\)(?:\\\\)*)\)'

# --------------------- BASE DECORATORS for ELEMENTS ---------------------------
def block(nest=Nesting.POST, subblock=None, subinline=None, opts=''):
  """
  Decorator for block style elements, to be used on a parser function.
  eg:

  ```python
  @block(...)
  def BlockName(text):
    \"\"\" docs for BlockName element go here \"\"\"
    return ['div', text]
  ```

  The name of the function becomes the name of the block. There is automatic
  sanitization/converstion that happens in the process.
  So `BlockName` would have `name='block-name'` so that it's easier to type
  in the plain-text format.
  """

  def block_fn(parser: Callable) -> Block:
    return Block(makename(parser.__name__),
              nest, subblock or ['all'], subinline or ['all'], parser, opts)

  return block_fn


def inlineone(regex, display=Display.INLINE, nest=Nesting.FRAME, subinline=None, escape=''):
  """
  Decorator for an inline element that has exactly one pattern and parser.
  For more complex inline elements, it's best to just define the element
  yourself.

  Recommended usage is to pass the regex is as a positional argument, and the
  others as kwargs, since it's hard to remember what order they go in.

  The parser function should take the groups of the returned regex as params,
  per usual and return html in s-expression form, like
  `['div', {'attr': 'value'}, 'text']`.

  """
  if subinline is None: subinline = ['inherit']

  def inline_fn(parser: Callable) -> Inline:
    r = re.compile(regex) if isinstance(regex,str) else regex
    i = Inline(makename(parser.__name__), display,
               nest, subinline, escape, [(r, parser)])
    return i

  return inline_fn


# ----------------- ELEMENT CREATOR HELPERS ----------------------------
def InlineFrame(name:str, escape:Union[str,Set[str]], parser):
  """
  A helper for inline frames, which have nesting type frame, and are ALWAYS
  subscribing to the style 'inherit'.
  The only things a frame needs to define is name, escape, and parser.
  """
  return Inline(name, Display.INLINE, Nesting.FRAME, ['inherit'], escape, parser)


def SingleGroupInlineFrame(name:str, start:str, end:str,
                           tag:str, attr:Mapping[str,str]=None):
  """
  A special kind of inline frame that has only one capture group and wraps
  it with some set of start and end characters.

  It's expected that this kind of element will wrap its contents in one tag
  with specified attributes, so you can pass in a tag and its attributes
  here directly and the parser function will be generated for you.

  The first character of `start` and `end` is added to the list of escapable
  letters, and the generated regex makes sure that neither the start nor the
  end of the pattern are preceded by a backslash for escape.
  """
  patt = re.compile(Patterns.single_group.value.format(
      re.escape(start), re.escape(end)))
  return InlineFrame(name, {start[0], end[0]},
    [(patt, lambda body: [tag, attr or {}, *body])])


def IdenticalInlineFrame(name:str, s:str, tag:str, attr:Mapping[str,str]=None):
  """
  A very simple wrapper around `SingleGroupInlineFrame` that will work
  if you expect the start/end of the element to be the same. Eg: `*bold*`.
  """
  return SingleGroupInlineFrame(name, s, s, tag, attr)


def MirrorInlineFrame(name:str, start:str, tag:str, attr:Mapping[str,str]=None):
  """
  A very simple wrapper around `SingleGroupInlineFrame` that is for when
  the start/end of the element are mirrors of each other, eg: `{++add++}`
  Handles ()[]{}<> flipping.
  """
  return SingleGroupInlineFrame(
    name, start,
    start[::-1].translate(str.maketrans('()[]{}<>', ')(][}{><')),
    tag, attr)


def specialized_link(designation:str):
  pattern = re.compile(Patterns.link.value.format(designation), re.V1)

  def wrapper(fn:Callable):
    return Inline(makename(fn.__name__), Display.INLINE, Nesting.POST, ['inherit'],
                  '()[]'+ designation[0] if len(designation) > 0 else '',
                  [(pattern, fn)])

  return wrapper
