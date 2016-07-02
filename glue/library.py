# File: glue/library.py
# Author: Vishesh Gupta
# Created: 31 May 2016

import regex as re
import toolz as t
import toolz.curried as tc
from itertools import zip_longest

from glue import Nesting, Registry
from glue.elements import IdenticalInlineFrame, MirrorInlineFrame
from glue.elements import specialized_link, inlineone, block, Display
from glue.elements import Patterns

# this module exposes basic elements and registries for common tasks.
# it's designed to have feature parity with markdown, or a more sensible
# version of markdown, if so desired.

# Registries exposed are:

# STANDARD INLINE - registry that has the standard definitions for rich text,
# such as
# bold, italic, monospace, underline, strikethrough
# link, tooltip
# headers

Bold = IdenticalInlineFrame('bold', '*', 'strong')
Italic = IdenticalInlineFrame('italic', '_', 'em')
Monospace = IdenticalInlineFrame('monospace', '`', 'code')
Underline = IdenticalInlineFrame('underline', '__', 'span',
  {'style': 'text-decoration:underline;'})
Strikethrough = IdenticalInlineFrame('strikethrough', '~', '')


@specialized_link('')
def Link(groups):
  return ['a', {'href': groups[1]}, groups[0]]

@specialized_link('T')
def Tooltip(groups):
  return ['span.tooltip', groups[0], ['div.tooltip-text', groups[1]]]

@inlineone(r'^(\#{1,6})([^\n]*)$', display=Display.BLOCK, nest=Nesting.POST, escape='#')
def Header(groups):
  return ['h' + str(len(groups[0])), groups[1]]

StandardInline = Registry(Bold, Italic, Monospace, Underline,
                          Strikethrough, Link, Tooltip)

# CRITIC - registry for doing annotations and critiques on the document.
# insertion, deletion, substitution (really deletion + insertion)
# highlighting, and comments.

CriticAdd = MirrorInlineFrame('critic-add', '{++', 'ins')
CriticDel = MirrorInlineFrame('critic-del', '{--', 'del')
CriticComment = MirrorInlineFrame('critic-comment', '{>>', 'span.critic.comment')
CriticHighlight = MirrorInlineFrame('critic-highlight', '{==', 'mark')

@inlineone(r'(?<!\\)(?:\\\\)*\K\{~~(.*?(?<!\\)(?:\\\\)*)~>(.*?(?<!\\)(?:\\\\)*)~~}', nest=Nesting.POST)
def CriticSub(groups):
  return [['ins', groups[0]],['del', groups[1]]]

CriticMarkup = Registry(CriticAdd, CriticDel, CriticComment, CriticHighlight, CriticSub)

# MARKDOWN - registry that contains standard definitions according to the
# markdown syntax style. These are *different* from the STANDARD definitions
# in that they have redundancy and aren't capable of showing off as many styles.
# bold, italic, monospace, link

# LISTS - blocks that allow defining lists.
# ordered list, unordered list, outline

# ---list
# as;fkjasdf
#   as;dkfjas
# a sfa sfas;fkj sdf
#   as;dkfljas
#   asfjas;kdfj
#     asdlfjasldfkj
# ...




# TABLES - blocks that result in some kind of tabular form
# table - basic table form
# sidebyside - 2 columns that are rendered independently
# flexbox - lays out things in a flex manner

@block()
def SideBySide(text):
  """A block for multicolumn layout in a row.
  Uses the `|` character to separate columns, escape pipe with \| in the body.
  The columns are processed as their own blocks, and they do not need to line up.
  """

  return t.pipe(text.split('\n'),
                tc.map(lambda x: re.split(' ?' + Patterns.escape.value.format('\|') + ' ?', x)),
                lambda x: zip_longest(*x, fillvalue=''),
                tc.map(lambda x: ['div', {'style': {'flex': '1'}}, '\n'.join(x)]),
                tc.cons({'style': {'display': 'flex'}}),
                tc.cons('div'))


# COMPONENTS - general purpose blocks for isomorphic-js components
# works well with react/mithril etc

# PHOTOS - displaying images
# image (inline like markdown)
# figures - images with captions, basically.
# annotated image - component library image processing

# STANDALONE - such as KaTeX and musicalabc, to name a few.


# CODE BLOCKS - styling these is really complicated for some reason
# web library integration - there are many
# pygments using native python
# julia formatter pseudocode (from Sexpr.jl)
# theoretical example of using regexes to make a code highlighter.


# TOPLEVEL - two options for what the top might look like
# such as doing nothing and returning a div, or parsing paragraphs, but
# excluding block elements

@block()
def NoopBlock(text):
  return ['div', text]

@block(nest=Nesting.SUB)
def Paragraphs(text):
  """
  Creates p tags from each blank line separated block of text.

  Any blocks of text with a blank line in between them (`\n\n` sequence) is
  separated and given its own `p` tag. This is the minimum formatting you'd
  probably expect in any static content generator.

  Subscribes to the entire registry.
  """
  return t.pipe(re.split(r'(?m)(?:\n|^)(\[\|\|\d+\|\|\])', text),
                tc.filter(lambda x: not not x),
                tc.map(lambda x: x if re.match(r'^\[\|\|\d+\|\|\]$',x) else ['p', x.rstrip()]),
                tc.cons('div'),
                list)

Standard = Registry(Paragraphs, top=Paragraphs) | StandardInline | CriticMarkup
