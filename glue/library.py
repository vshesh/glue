# File: glue/library.py
# Author: Vishesh Gupta
# Created: 31 May 2016

import regex as re
import toolz as t

from glue import inlineone, Nesting, Inline, block
from glue.elements import IdenticalInlineFrame, MirrorInlineFrame, Patterns

# this module exposes basic elements and registries for common tasks.
# it's designed to have feature parity with markdown, or a more sensible
# version of markdown, if so desired.

# Registries exposed are:

# STANDARD INLINE - registry that has the standard definitions for rich text,
# such as
# bold, italic, monospace, underline, strikethrough
# link, tooltip

Bold = IdenticalInlineFrame('bold', '*', 'strong')
Italic = IdenticalInlineFrame('italic', '_', 'em')
Monospace = IdenticalInlineFrame('monospace', '`', 'code')
Underline = IdenticalInlineFrame('underline', '__', 'span',
  {'style': 'text-decoration:underline;'})
Strikethrough = IdenticalInlineFrame('strikethrough', '~', '')

Link = Inline('link', Nesting.POST, ['inherit'], '()[]',
  [(re.compile(Patterns.link.value.format('')),
   lambda groups: ['a', {'href': groups[1]}, groups[0]])])


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

# MARKDOWN - registry that contains standard definitions according to the
# markdown syntax style. These are *different* from the STANDARD definitions
# in that they have redundancy and aren't capable of showing off as many styles.
# bold, italic, monospace, link

# LISTS - blocks that allow defining lists.
# ordered list, unordered list, outline

# TABLES - blocks that result in some kind of tabular form
# table - basic table form
# sidebyside - 2 columns that are rendered independently
# flexbox - lays out things in a flex manner
#

# COMPONENTS - general purpose blocks for isomorphic-js components
# works well with react/mithril etc

# PHOTOS - displaying images
# image (inline like markdown)
# annotated image - component library image processing
# figures - images with captions, basically.

# STANDALONE - such as KaTeX and musicalabc, to name a few.

# CODE BLOCKS - styling these is really complicated for some reason
# web library integration
# julia formatter pseudocode (from Sexpr.jl)


# TOPLEVEL - two options for what the top might look like
# such as doing nothing and returning a div, or parsing paragraphs, but
# excluding block elements

@block()
def NoopBlock(text):
  """
  Block wraps contents with a div, and subscribes to the entire registry.
  """
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
  return list(t.cons('div', t.map(lambda x: x if x.startswith('[||') else ['p', x.strip()], text.split('\n\n'))))