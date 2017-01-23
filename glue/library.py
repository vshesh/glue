# File: glue/library.py
# Author: Vishesh Gupta
# Created: 31 May 2016

import uuid

import functools
import simplejson as json
import ruamel.yaml as yaml
import regex as re
import toolz as t
import toolz.curried as tc
from itertools import zip_longest

from glue import Nesting, Registry
from glue.elements import *

# this module exposes basic elements and registries for common tasks.
# it's designed to have feature parity with markdown, or a more sensible
# version of markdown (called STANDARD), if so desired.

# Registries exposed are:

# STANDARD INLINE - registry that has the standard definitions for rich text,
# such as
# bold, italic, monospace, underline, strikethrough
# link, tooltip
# headers

Bold = IdenticalInline('bold', '*', 'strong')
Italic = IdenticalInline('italic', '_', 'em')
Monospace = IdenticalInline('monospace', '`', 'code')
Underline = IdenticalInline('underline', '__', 'span',
                            {'style': 'text-decoration:underline;'})
Strikethrough = IdenticalInline('strikethrough', '~', 'del')

Superscript = SingleGroupInline('superscript', '^{', '}', 'sup')
Subscript = SingleGroupInline('subscript', '_{', '}', 'sub')

@link('')
def Link(groups):
  return ['a', {'href': groups[1]}, groups[0]]

@link('!!')
def InlineImage(groups):
  return ['img', {'alt': groups[0], 'src': groups[1],
                  'style': {'display': 'inline-block',
                            'vertical-align': 'middle',
                            'max-width': '100%'}}]

@link('!')
def FullImage(groups):
  return ['img', {'alt': groups[0], 'src': groups[1],
                  'style': {'margin': '0 auto', 'display': 'block',
                            'max-width': '100%'}}]

@asset_inline(AssetType.CSS, '''
.pictogram {
  position: relative;
}
.pictogram > img {
  height: 1.5em;
  vertical-align: middle;
}
.pictogram > span.pictoword {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0,0,0,0.4);
  color: white;
  display: none;
  font-size: 75%;
}
.pictogram:hover > .pictoword {
  display: inline;
}
''')
@link('P')
def Pictogram(groups):
  return ['span.pictogram',
          ['img', {'alt': groups[0], 'src': groups[1]}],
          ['span.pictoword', groups[0]]]

@asset_inline(AssetType.CSS, '''
  .tooltip {
      position: relative;
      display: inline-block;
      border-bottom: 1px dotted black;
  }

  .tooltip .tooltip-text {
      visibility: hidden;
      min-width: 100%;
      background-color: black;
      color: #fff;
      text-align: center;
      border-radius: 6px;
      padding: 5px;
      position: absolute;
      z-index: 1;
      bottom: 100%;
      left: 50%;
      transform: translateX(-50%) translateY(-5px);
  }

  .tooltip .tooltip-text::after {
      content: "";
      position: absolute;
      top: 100%;
      left: 50%;
      margin-left: -5px;
      border-width: 5px;
      border-style: solid;
      border-color: black transparent transparent transparent;
  }

  .tooltip:hover .tooltip-text {
      visibility: visible;
  }
  ''')
@link('T')
def Tooltip(groups):
  return ['span.tooltip', groups[0], ['div.tooltip-text', groups[1]]]

@inline(r'^(\#{1,6})([^\n]*)$', display=Display.BLOCK, nest=Nesting.POST, escape='#')
def Header(groups):
  return ['h' + str(len(groups[0])),
          ['a', {'name':  re.sub(r'[^A-Za-z0-9 ]', '', groups[1]).strip().replace(' ', '-').lower()},
           groups[1].lstrip()]]

StandardInline = Registry(Bold, Underline, Superscript, Subscript, Italic, Monospace,
                          Strikethrough, Link, InlineImage, FullImage, Pictogram, Tooltip, Header)

# CRITIC - registry for doing annotations and critiques on the document.
# insertion, deletion, substitution (really deletion + insertion)
# highlighting, and comments.

CriticAdd = MirrorInline('critic-add', '{++', 'ins')
CriticDel = MirrorInline('critic-del', '{--', 'del')
CriticComment = MirrorInline('critic-comment', '{>>', 'span.critic.comment')
CriticHighlight = MirrorInline('critic-highlight', '{==', 'mark')

@inline_two('{~~', '~>', '~~\}', nest=Nesting.POST)
def CriticSub(groups):
  return [['del', groups[0]],['ins', groups[1]]]

CriticMarkup = Registry(CriticSub, CriticAdd, CriticDel, CriticComment, CriticHighlight)

# MARKDOWN - registry that contains standard definitions according to the
# markdown syntax style. These are *different* from the STANDARD definitions
# in that they have redundancy and aren't capable of showing off as many styles.
# bold, italic, monospace, link

MDStarBold = MirrorInline('md-star-bold', '**', 'strong')
MDLodashBold = MirrorInline('md-lodash-bold', '__', 'strong')
MDStarItalic = MirrorInline('md-star-italic', '*', 'em')
MDLodashItalic = MirrorInline('md-lodash-italic', '_', 'em')

MarkdownInline = (StandardInline - [Bold, Italic, Underline]) + [
  MDStarBold, MDLodashBold, MDStarItalic, MDLodashItalic]

# Standard Blocks:

@asset_inline(AssetType.CSS, '''
.blockquote {
  margin-left: 10px;
  padding-left: 5px;
  font-size: 150%;
  border-left: 5px solid gray;
}''')
@block(Nesting.SUB)
def Blockquote(text: str):
  r = Paragraphs(text)
  r[0] += '.blockquote'
  return r

# LISTS - blocks that allow defining lists.
# ordered list, unordered list, outline


def process_list(l, root: str='ul'):
  """

  :param l: a list like the one returned by the below `List` element.
  :param root: what element wraps the list (`ul`, `ol`, etc).
  :return: HTML that represents the list `l`. (cottonmouth style).
  """
  if isinstance(l[0], list):
    raise NotImplementedError('Sublist found as first element of the list. '
      'Sublists must come after another list element, as per the HTML5 spec.')
  acc = [root]
  for e in l:
    if isinstance(e, str):
      acc.append(['li', e])
    elif isinstance(e, list):
      acc[-1].append(process_list(e, root))
  return acc

@block(opts="o")
def List(text, o:bool=False):
  """
  Basic unordered list - should just output a `ul` element with `li` underneath.
  Nested lists are handled, and >2 spaces of indentation will start a sublist.
  This list element does NOT allow for any kind of 'bullet' in front of the items
  as of now.

  Example:
    ---list
    as;fkjasdf
      as;dkfjas
    a sfa sfas;fkj sdf
      as;dkfljas
      asfjas;kdfj
        asdlfjasldfkj
    ...

  :param text: body text of the list
  :param o: whether list is ordered, in which case an `ol` is returned instead of a `ul`.
  to the ul or ol type of element.
  :return: a list element
  """
  items = []
  pos = [-1]
  for line in text.split('\n'):
    if line.strip() == "": continue
    p = len(line) - len(line.lstrip(' '))
    if p > pos[-1]:
      items.append([line.strip()])
      pos.append(p)
    elif p < pos[-1]:
      while p < pos[-1]:
        item = items.pop()
        items[-1].append(item)
        pos.pop()
      items[-1].append(line.strip())
      pos.append(p)
    else:
      items[-1].append(line.strip())
  # turtle down remaining lists.
  while len(items) > 1:
    items[-2].append(items[-1])
    items.pop()

  return process_list(items[0], 'ol' if o else 'ul')


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
  return t.pipe(text.rstrip('\n').split('\n'),
                tc.map(lambda x: re.split(' ?' + Patterns.escape.value.format('\|') + ' ?', x)),
                lambda x: zip_longest(*x, fillvalue=''),
                tc.map(lambda x: ['div', {'style': {'flex': '1'}}, '\n'.join(x)]),
                tc.cons({'style': {'display': 'flex'}}),
                tc.cons('div'),
                list)

@asset_inline(AssetType.CSS, '.matrix {margin: 0 auto}')
@block()
def Matrix(text, type='flex'):
  """Displays a table or flexbox style grid of values.
  For flexbox mode, make sure that there are an equal number of | in each row.
  Table mode is more flexible.
  """
  return t.pipe(text.split('\n'),
                tc.map(lambda x: re.split(' ?' + Patterns.escape.value.format('\|') + ' ?', x)),
                tc.map(lambda x: ['div' if type == 'flex' else 'tr',
                                  {'style': {'display':'flex'} if type == 'flex' else {}},
                                  *t.map(lambda y: ['span' if type == 'flex' else 'td', {'style': {'flex': 1}} if type == 'flex' else {}, y], x)]),
                tc.cons('div.matrix.matrix-flex' if type == 'flex' else 'table.matrix.matrix-table'),
                list)


# MEDIA - displaying images
# image (inline like markdown) (see above)
# multi-image - side by side images that have the same height despite not having
#               the same aspect ratio. Can also take captions for each image.
#               This is way harder than it looks without knowing the aspect ratio
#               of each image before hand.

# figures - images with captions, basically.
# annotated image - component library image processing

@block()
def Figure(text):
  split = text.split('\n', maxsplit=1)
  if len(split) == 1:
    caption = None
    body = split[0]
  else: #len(split) == 2
    caption, body = split
  return ['figure', body, (['figcaption', caption] if caption else None)]

# audio - show an audio file, with html5 audio element (inline)
# wavesurfer - audio with waveforms rendered to a div

@inline('@\\{(.+?'+Patterns.escape.value.format(')\\}'), nest=Nesting.NONE)
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

@asset_inline(AssetType.CSS, '.katex {position: relative;}')
@asset_url(AssetType.CSS, 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css')
@asset_url(AssetType.JS, 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js')
@standalone_integration()
def Katex(text, docid, elem):
  """Integration with Khan Academy's math typsetting library.
  Takes just the body text (which is the math) and renders it in place using
  the API of the library.
  """
  return repr("katex.render('\\displaystyle{{{0}}}', {1})".format(text.strip(), elem))[1:-1]


# CODE BLOCKS - styling these is really complicated for some reason
# web library integration - there are many (hightlight.js is a good example)
# pygments using native python
# julia formatter pseudocode (from Sexpr.jl)
# theoretical example of using regexes to make a code highlighter.

@block()
def CodeBySide(text, language='md'):
  """
  A nifty component for showing off GLUE examples. Will render anything you
  put in the environment per usual, and also display the raw text in a code box
  to the side in a flex layout. It can be done manually with side-by-side, but
  that required repeating yourself. This component allows you to be DRY about it.

  Note that this component has a dependency on the existence of the `Code`
  component.

  :param text: body text of the component
  :param language: programming language to display the insides in. markdown is
                   default to accommodate glue components.
  :return: a flex-box row with a rendered component, and the code to make it
           happen side by side.
  """
  return ['div', {'style': {'display': 'flex', 'align-items': 'center'}},
          ['div', {'style': {'flex': 1}}, text],
          ['div', {'style': {'flex': 1}}, '---code ' + language + '\n' + text.rstrip('\n') + '\n...']]

@asset_url(AssetType.CSS, "//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.8.0/styles/atom-one-light.min.css")
@asset_url(AssetType.JS, "//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.8.0/languages/julia.min.js")
@asset_url(AssetType.JS, "//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.8.0/languages/haskell.min.js")
@asset_url(AssetType.JS, "//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.8.0/highlight.min.js")
@terminal_block()
def Code(text, language='python'):
  """
  Code block with highlight.js
  :param text: the code block, which will be represented verbatim
  :param language: programming language that has to be supported by highlight.js
  :return: HTML code that will render a nice syntax highlighted code block.
  """
  h = str(uuid.uuid4())
  return ['pre', ['code#{0}.language-{1}'.format(h, language), text],
                 ['script', {'key': h},
                  "hljs.highlightBlock(document.getElementById('{0}'))".format(h)]]

@asset_inline(AssetType.CSS, '''
  .annotated-code .code-box {
    display: flex;
  }
  .annotated-code .code-box > pre {
    flex: 1;
    margin: 0;
  }
  .annotated-code .code-box pre:first-child {
    flex: 0;
    padding-top: 0.5em;
  }
  .annotated-code .code-box pre:first-child span {
    padding: 0 3px;
  }
  .annotated-code .code-box pre:first-child span:hover {
    background-color: black;
    color: white;
  }
''')
@asset_url(AssetType.JS, '/js/annotated-code.js')
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
  js view library out of it. `name` must be camel case, and upper case, for it to be
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

@asset_inline(AssetType.CSS, '''
.chordChart g.grid {stroke: black; stroke-width: 1px;}
.chordChart text.labels {fill: white;}
''')
@asset_url(AssetType.JS, '/js/chordography.js')
@standalone_integration(inner_elem='svg')
def GuitarChord(text, docid, elem):
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
  info = yaml.safe_load(text)
  return repr("chordMaker()({0}, {1})".format(elem, repr(info)))[1:-1]

@asset_inline(AssetType.JS, '''
function getStyleProp(elem, prop){
  if(window.getComputedStyle)
      return window.getComputedStyle(elem, null).getPropertyValue(prop);
  else if(elem.currentStyle) return elem.currentStyle[prop]; //IE
}

function setViewBox(selector) {
  var el = document.getElementById(selector);

  var height = parseFloat(getStyleProp(el, 'height'));
  var width = parseFloat(getStyleProp(el, 'width'));
  el.removeAttribute('style');
  var svg = el.firstChild;
  svg.setAttribute("viewBox", "0 0 " + width + " " + height);
  svg.removeAttribute("height");
  svg.removeAttribute("width");
}
''')
@asset_url(AssetType.JS, 'https://rawgit.com/paulrosen/abcjs/master/bin/abcjs_basic_midi_3.0-min.js')
@standalone_integration()
def MusicalAbc(text, docid, elem):
  """Integration with musical abc, a lightweight sheet music syntax.
  see https://github.com/paulrosen/abcjs.
  """
  return "ABCJS.renderAbc({0}, {1}); setViewBox('{2}');".format(elem, repr(text), docid)


Music = Registry(GuitarChord, MusicalAbc)

# Domain Specific Blocks - Charts! (using SVG, with or without D3/paths.js)


# Registry setup

Standard = Registry(Paragraphs, top=Paragraphs) | StandardInline | CriticMarkup + [Blockquote, List, CodeBySide, SideBySide, Matrix, Katex, Figure, Audio, MusicalAbc, GuitarChord, Code, AnnotatedCode, JsonComponent, YamlComponent]
Markdown = Registry(Paragraphs, top=Paragraphs) | MarkdownInline | CriticMarkup
