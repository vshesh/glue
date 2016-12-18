# File: glue/library.py
# Author: Vishesh Gupta
# Created: 31 May 2016

import uuid
import simplejson as json
import yaml
import regex as re
import toolz as t
import toolz.curried as tc
from itertools import zip_longest

from glue import Nesting, Registry
from glue.elements import IdenticalInlineFrame, MirrorInlineFrame, \
  terminal_block
from glue.elements import link, inline, inline_two, block, Display
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
Strikethrough = IdenticalInlineFrame('strikethrough', '~', 'del')

@link('')
def Link(groups):
  return ['a', {'href': groups[1]}, groups[0]]

@link('!')
def FullImage(groups):
  return ['img', {'alt': groups[0], 'src': groups[1], 'style': {'margin': '0 auto', 'display': 'block', 'max-width': '100%'}}]

@link('P')
def Pictogram(groups):
  return ['span.pictogram',
          ['img', {'alt': groups[0], 'src': groups[1]}],
          ['span.pictoword', groups[0]]]

@link('T')
def Tooltip(groups):
  return ['span.tooltip', groups[0], ['div.tooltip-text', groups[1]]]

@inline(r'^(\#{1,6})([^\n]*)$', display=Display.BLOCK, nest=Nesting.POST, escape='#')
def Header(groups):
  return ['h' + str(len(groups[0])), groups[1].lstrip()]

StandardInline = Registry(Bold, Underline, Italic, Monospace,
                          Strikethrough, FullImage, Pictogram, Tooltip, Header)

# CRITIC - registry for doing annotations and critiques on the document.
# insertion, deletion, substitution (really deletion + insertion)
# highlighting, and comments.

CriticAdd = MirrorInlineFrame('critic-add', '{++', 'ins')
CriticDel = MirrorInlineFrame('critic-del', '{--', 'del')
CriticComment = MirrorInlineFrame('critic-comment', '{>>', 'span.critic.comment')
CriticHighlight = MirrorInlineFrame('critic-highlight', '{==', 'mark')

@inline_two('{~~', '~>', '~~\}', nest=Nesting.POST)
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
                tc.cons('div'),
                list)

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


# MEDIA - displaying images
# image (inline like markdown) (see above)
# multi-image - side by side images that have the same height despite not having
#               the same aspect ratio. Can also take captions for each image.
#               This is way harder than it looks without knowing the aspect ratio
#               of each image before hand.

# figures - images with captions, basically.
# annotated image - component library image processing

# audio - show an audio file, with html5 audio element (inline)
# wavesurfer - audio with waveforms rendered to a div

@block(nest=Nesting.FRAME, sub=["inline"])
def Figure(text, caption=''):
  return ['figure', text, ['figcaption', caption] if caption else None]

@inline('@\\[(.+?'+Patterns.escape.value.format(')\\]'), nest=Nesting.NONE)
def Audio(group):
  """
  `@[audio file]` creates an inline audio element with the HTML5 audio tag.
  :param group: The audio file should be in group[0],
   since there's only one capture group.
  :return: audio tag with the file. proper defaults are set in case audio is not
   supported on the user's browser.
  """
  return ['audio',{'controls': True, 'src': group[0]},
          'Audio is not supported on your browser.']

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

@terminal_block()
def Katex(text):
  """Integration with Khan Academy's math typsetting library.
  Takes just the body text (which is the math) and renders it in place using
  the API of the library.
  """
  h = str(uuid.uuid4())
  elem = "document.getElementById('katex-{0}')".format(h)
  return ['div#katex-{0}'.format(h),
          ['script', {'key': h},
           repr("katex.render('\\displaystyle{{{0}}}', {1})".format(text.strip(), elem))[1:-1]]]


# CODE BLOCKS - styling these is really complicated for some reason
# web library integration - there are many (hightlight.js is a good example)
# pygments using native python
# julia formatter pseudocode (from Sexpr.jl)
# theoretical example of using regexes to make a code highlighter.

@terminal_block()
def Code(text, language='python'):
  """
  Code block with highlight.js
  :param text: the code block, which will be represented verbatim
  :param language: programming language that has to be supported by highlight.js
  :return: HTML code that will render a nice syntax highlighted code block.
  """
  h = str(uuid.uuid4())
  return ['pre', ['code#{0}'.format(h), {'class': 'language-' + language}, text],
                 ['script', {'key': h},
                  "hljs.highlightBlock(document.getElementById('{0}'))".format(h)]]

@terminal_block()
def AnnotatedCode(text, language='python', comment='#'):
  """
  A block that generates a code block where the comments are folded into
  annotations that are revealed when hovered over.
  See: [here](http://jsbin.com/gixaxefasu/edit?js,output) for an example.

  Requires a CSS and JS asset to be included in index.html (as of now). The JS
  component & CSS styles are available at the jsbin link above. See `index.html`

  :param text: body text of the block
  :param language: programming language the code is in
  :param comment: the string that starts a comment in this language
  """
  total_annotation_lines = 0
  code = ''
  annotations = {}
  annotation = ''
  for (num,line) in enumerate(text.split('\n')):
    if line.lstrip().startswith(comment):
      total_annotation_lines += 1
      a = line.lstrip()[len(comment):].lstrip()
      # only add the annotation if there is actual text in the comment.
      if len(a.strip()) > 0: annotation += a + '\n'
    else:
      code += line + '\n'
      if len(annotation) > 0:
        annotations[num - total_annotation_lines] = annotation
        annotation = ''
  return ['AnnotatedCode', {'code': code.rstrip(), 'annotations': annotations, 'language': language}]

# TOPLEVEL - two options for what the top might look like
# such as doing nothing and returning a div, or parsing paragraphs, but
# excluding block elements

@block()
def NoopBlock(text):
  """A "noop" in the case of generating html means wrapping the text in a div
  and returning it. The most basic possible block.

  This block can be a good choice for a top-level entity if writing something
  that isn't intended to have paragraphs in it and is divided some other way.

  Or if you intend to just deal with everything as one large block, this works
  well too.
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
  return t.pipe(re.split(r'(?m)(?:\n|^)(\[\|\|\d+\|\|\])', text),
                tc.mapcat(lambda x: x.split('\n\n')),
                tc.filter(lambda x: not not x),
                tc.map(lambda x: x if re.match(r'^\[\|\|\d+\|\|\]$',x) else ['p', x.rstrip()]),
                tc.cons('div'),
                list)

# COMPONENT (in a view library, say React or mithril)

@terminal_block()
def YamlComponent(text, name):
  """
  You can specify your props using the YAML syntax, and create a component in a
  view library out of it. `name` must be camel case, and upper case, for it to be
  recognized properly by this library.

  :param text: The YAML formatted props to the component
  :param name: name of the component like `AnnotatedCode`
  :return: [name, props] -> syntax that represents this component with these props.
  """
  props = yaml.safe_load(text)
  return [name, props]

@terminal_block()
def JsonComponent(text, name):
  props = json.loads(text)
  return [name, props]

# Domain Specific Blocks -> MUSIC related:

@terminal_block()
def GuitarChord(text):
  """
  Creates an svg element that draws a guitar chord based on chordography's api.

  :param text: The body of the guitar chord element has up to three lines in
   YAML syntax:
   ```
   title: C7b9
   fret: x 1 1 4 5 1
   label: x 1 1 3 4 1
   ```
   Only the line that says "fret" is necessary, per the chordography api.
  :return: the html scaffolding with a small script tag injected that will
   generate the desired chord diagram.
  """
  h = str(uuid.uuid4())
  elem = "document.getElementById('guitar-chord-{0}')".format(h)
  info = yaml.safe_load(text)
  return ['div',
          ['div#guitar-chord-{0}'.format(h)],
          ['script', {'key': h},
           repr(
             "chordMaker()({0}, {1})".format(elem, repr(info)))[1:-1]]]

@terminal_block()
def MusicalAbc(text):
  """Integration with musical abc, a lightweight sheet music syntax.
  see https://github.com/paulrosen/abcjs.
  """
  # TODO(vshesh): abcjs uses a fixed-width svg -
  # make it into a viewBox with variable outside width!
  # https://github.com/paulrosen/abcjs/issues/71
  h = 'musical-abc-' + str(uuid.uuid4())
  elem = "document.getElementById('{0}')".format(h)
  return ['div',
          ['div#{0}'.format(h)],
          ['script', {'key': h},
             "ABCJS.renderAbc({0}, {1});".format(elem, repr(text))]]

Music = Registry(GuitarChord, MusicalAbc)

# Domain Specific Blocks - Charts! (using SVG, with or without D3/paths.js)


# Registry setup

Standard = Registry(Paragraphs, top=Paragraphs) | StandardInline | CriticMarkup + [SideBySide, Katex, Audio, MusicalAbc, GuitarChord, Code, AnnotatedCode]
Markdown = Registry(Paragraphs, top=Paragraphs) | MarkdownInline | CriticMarkup

