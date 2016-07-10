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
# version of markdown (called STANDARD), if so desired.

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
  return ['h' + str(len(groups[0])), groups[1].lstrip()]

StandardInline = Registry(Bold, Italic, Monospace, Underline,
                          Strikethrough, Link, Tooltip, Header)

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

MDStarBold = MirrorInlineFrame('md-star-bold', '**', 'strong')
MDLodashBold = MirrorInlineFrame('md-lodash-bold', '__', 'strong')
MDStarItalic = MirrorInlineFrame('md-star-italic', '*', 'em')
MDLodashItalic = MirrorInlineFrame('md-lodash-italic', '_', 'em')

MarkdownInline = (StandardInline - [Bold, Italic]) + [
  MDStarBold, MDLodashBold, MDStarItalic, MDLodashItalic]

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
# matrix - every line is a row, and pipes separate columns, rendered in flexbox again.

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

@block()
def Matrix(text, type='flex'):
  """Displays a table or flexbox style grid of values.
  For flexbox mode, make sure that there are an equal number of | in each row.
  Table mode is more flexible.
  """
  return t.pipe(text.split('\n'),
                tc.map(lambda x: re.split(' ?' + Patterns.escape.value.format('\|') + ' ?', x)),
                tc.map(lambda x: ['div' if type == 'flex' else 'tr',
                                  {'style': {'display':'flex'}},
                                  *t.map(lambda y: ['span' if type == 'flex' else 'td', {'flex': 1}, y], x)]),
                tc.cons({'class': 'matrix matrix-flex' if type == 'flex' else 'matrix matrix-table'}),
                tc.cons('div' if type == 'flex' else 'table'))

# COMPONENTS - general purpose blocks for isomorphic-js components
# works well with react/mithril etc

# PHOTOS - displaying images
# image (inline like markdown)
# figures - images with captions, basically.
# annotated image - component library image processing

# STANDALONE - such as KaTeX and musicalabc, to name a few.

# the few general strategies here are:
# 1. render server-side: this would work a lot better if I was writing this
#    library in JS rather than python. Starting a node process to render
#    something might be nice but probably is going to make the rendering process
#    slow, especially for pages with a lot of math.
# 2. generate an element with a script that will render the math into the element
#    May result in strange looking divs with js embedded in them, not necessarily ideal,
#    but very fast, and mirrors the API online for a lot of parser JS libraries
# 3. Depend on some component library to do the generation.
#    Fast also, and has less cruft, but then requires you use react/mithril/etc

# #2 is the best compromise and that is what is included with the standard library.

@block(nest=Nesting.NONE, subinline=[], subblock=[])
def Katex(text):
  h = hash(text)
  return ['div#{0}'.format(h),
          ['script', 'katex.render({0}, {1})'.format(text, 'document.getElementById({0})'.format(h))]]



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
  print(repr(text), text)
  return t.pipe(re.split(r'(?m)(?:\n|^)(\[\|\|\d+\|\|\])', text),
                tc.mapcat(lambda x: x.split('\n\n')),
                tc.filter(lambda x: not not x),
                tc.map(lambda x: x if re.match(r'^\[\|\|\d+\|\|\]$',x) else ['p', x.rstrip()]),
                tc.cons('div'),
                list)

Standard = Registry(Paragraphs, top=Paragraphs) | StandardInline | CriticMarkup
Markdown = Registry(Paragraphs, top=Paragraphs) | MarkdownInline | CriticMarkup
