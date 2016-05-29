#/usr/bin/env python3
from typing import Mapping, List, Union, Set
from functools import wraps
from enum import Enum
from collections import namedtuple as nt

import regex as re
import inflection
import toolz as t


Nesting = Enum('Nesting', 'FRAME POST SUB NONE')
# ------------------  BASE ELEMENTS --------------------------

Block = nt('Block',
           ['name', 'nest', 'nesti', 'subblock', 'subinline', 'parser'])
Block.__call__ = lambda self, *args, **kwargs: self.parser(*args, **kwargs)
Block.__hash__ = lambda self: self.name.__hash__()
Block.__doc__ = """
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

`nestb`/`nesti` are the nesting policies for nesting blocks and inline elements,
respectively. As of now, only `nestb` works, and it is the nesting policy
for both. This will probably be changed in the future, as soon as I identify
an actual use case where someone would want a different inline policy.

`subblock` is an array of names or literal block elements that this block
accepts as sub-blocks. In general, most blocks will either be `Nesting.NONE` or
accept every block, but you can be more specific if you'd like.

`subinline` is the same for inline elements.

`parser` is a function that takes string text and outputs html corresponding
to whatever this block would like to parse.
"""

Inline = nt('Inline', ['name', 'nest', 'subinline', 'escape', 'parser'])
Inline.__hash__ = lambda self: self.name.__hash__()
Inline.__doc__ = """
Base class for elements that are meant to be inline in the text inside blocks.
An inline element is expected to render in the style of an html `span` element.

The representation of an inline element in plaintext is defined by the parser
object, which is designed differently than the parser element of a block.
The parser in an Inline element looks like a list of pairs, where the first
element in a pair is a regex and the second is a function that takes the
recorded groups of the regex and returns an html element, in cottonmouth form.

It's recommended to use the more advanced `regex` library that comes from
pip so that you can properly create regexes that allow escaped characters.

Eg, matching bold text might seem easy (`\*(.*?)\*`) but it is actually quite
complicated to ignore a literal `\*` in the text.
For very basic things, both helper methods and standard elements have been
provided so you don't have to write them yourself!

`nest` defines what nesting style the parser is expecting. `FRAME` is the most
common, and basically "passes through" parsing from the parent block element.
However, you can also define `POST` or `SUB` if you expect to do some of
your own parsing (eg, link elements work well with the `POST` style).

`subscribe` is a list of either strings or literal element objects that define
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


# --------------------- DECORATORS for ELEMENTS ---------------------------
def block(nest=Nesting.POST, nesti=Nesting.POST,subblock=None, subinline=None):
  """
  Decorator for block style elements, to be used on a parser function.
  eg:

  ```python
  @block(...)
  def BlockName(text):
    \"\"\" docs for BlockName element go here \"\"\"
    return ['div', text]
  ```

  The name of the function is the name of the block, and the parser for a block
  should always take just one argument, which is the text (for now).
  The block name is changed so that it's made into a dash-separated name.
  So `BlockName` would have `name='block-name'` so that it's easier to type
  in the plain-text format.
  """

  def block_fn(parser):
    b = Block(inflection.dasherize(inflection.underscore(parser.__name__)),
              nest, nesti, subblock or ['all'], subinline or ['all'], parser)
    return b

  return block_fn


def inlineone(regex, nest=Nesting.FRAME, subscribe=None, escape=''):
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
  if subscribe is None: subscribe = ['inherit']

  def inline_fn(parser):
    i = Inline(inflection.dasherize(inflection.underscore(parser.__name__)),
               nest, subscribe, escape, [(regex, parser)])
    return i

  return inline_fn


# ----------------- ELEMENT CREATOR HELPERS ----------------------------
def InlineFrame(name:str, escape:Union[str,Set[str]], parser):
  """
  A helper for inline frames, which have nesting type frame, and are ALWAYS
  subscribing to the style 'inherit'.
  The only things a frame needs to define is name, escape, and parser.
  """
  return Inline(name, Nesting.FRAME, ['inherit'], escape, parser)


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
  patt = re.compile(
    '(?<!\\\\)(?:\\\\\\\\)*\\K{0}(.*?(?<!\\\\)(?:\\\\\\\\)*){1}'.format(
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

# -------------------------- BASIC SAMPLE ELEMENTS ----------------------
Bold = IdenticalInlineFrame('bold', '*', 'strong')
Italic = IdenticalInlineFrame('italic', '_', 'em')
Monospace = IdenticalInlineFrame('monospace', '`', 'code')
Underline = IdenticalInlineFrame('underline', '__', 'span',
  {'style': 'text-decoration:underline;'})

CriticAdd = MirrorInlineFrame('critic-add', '{++', 'ins')
CriticDel = MirrorInlineFrame('critic-del', '{--', 'del')
CriticComment = MirrorInlineFrame('critic-comment', '{>>', 'span.critic.comment')
CriticHighlight = MirrorInlineFrame('critic-highlight', '{==', 'mark')

Link = Inline('link', Nesting.POST, 'inherit', '()[]',
  [(re.compile(
    r'(?<!\\)(?:\\\\)*\K\[(.*?(?<!\\)(?:\\\\)*)\]\((.*?(?<!\\)(?:\\\\)*)\)'),
   lambda groups: ['a', {'href': groups[1]}, groups[0]])])

@block()
def NoopBlock(body):
  """
  Block does nothing, it just wraps contents with a div, and subscribes to the
  entire registry.
  """
  return ['div', *body]

@block()
def Paragraphs(text):
  """
  Any blocks of text with a blank line in between them (`\n\n` sequence) is
  separated and given its own `p` tag. This is the minimum formatting you'd
  probably expect in any static content generator.

  Subscribes to the entire registry.
  """
  return list(t.cons('div', t.map(lambda x: ['p', x.strip()], text.split('\n\n'))))
