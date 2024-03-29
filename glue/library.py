# File: glue/library.py
# Author: Vishesh Gupta
# Created: 31 May 2016
import regex as re
import simplejson as json
import ruamel.yaml as yaml
import toolz as t
import toolz.curried as tc
from itertools import zip_longest
from datetime import datetime

from glue import Registry
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


@inline(Patterns.tag_simple.value, nest=Nesting.POST)
def TagBasic(groups):
  return [groups[0]+(groups[1] or ''), groups[2]]

@inline(Patterns.tag_attributes.value, nest=Nesting.POST)
def TagAttributes(groups):
  return [groups[0]+ (groups[1] or ''), {x[0]:x[1] for x in t.partition(2, groups[2:-1])}, groups[-1]]

@asset_inline(AssetType.JS, '''
const Link = {
  view: ({attrs: {href, text}}) => m(m.route.Link, {href}, text)
}
''')
@link('M')
def MithrilLink(groups):
  return ['Link', {'href': groups[1], 'text': groups[0]}]

@link('')
def Link(groups):
  return ['a',
    {'href': groups[1],
     'target': '_blank' if groups[1].startswith('http') else '_self'},
    groups[0]]

@link('!!')
def InlineImage(groups):
  return ['img.inline-image', {'alt': groups[0], 'src': groups[1],
                  'style': {'display': 'inline-block',
                            'vertical-align': 'middle',
                            'max-width': '100%'}}]

@link('!')
def FullImage(groups):
  '''An image that takes up the full width of the page.'''
  return ['img.full-image', {'alt': groups[0], 'src': groups[1],
                  'style': {'margin': '0 auto', 'display': 'block',
                            'max-width': '100%'}}]

@asset_inline(AssetType.CSS, '''
@media only screen and (min-width: 750px) {
  p.stacked {
    white-space: nowrap;
    text-align: center;  }
  p.stacked span {
    vertical-align: middle;  }

  p.stacked .stack {
    display: inline-flex;
    flex-direction: column;
    margin: 0 0.5em;}

  p.stacked .stack span {
    text-align: center;
    font-weight: 500;  }
}
@media only screen and (max-width: 750px) {
  p.stacked .stack span::after {
    content: ", " }
  
  p.stacked .stack span:last-child::after,
  p.stacked .stack span:first-child::before {
    content: " " }
  p.stacked .stack span:last-child::before {
      content: "and"}
}''')
@block()
def Stacked(text):
  '''Creates a stacked sentence as in Artful Language by Tufte and his wife.'''
  return ['p.stacked',
          *[['span.stack', *[['span', phrase] for phrase in line[2:].split(',')]]
            if line.startswith('$#')
            else ['span', line] for line in text.split('\n')]]

@link(r'\.')
def Classed(groups):
  '''
  .[class1 class2](text) => ['span', {class: 'class1 class2'}, 'text']
  '''
  return ['span', {'class': groups[0]}, groups[1]]

@asset_inline(AssetType.CSS, '''
.pictogram {
  position: relative;
}
.pictogram > img {
  max-height: 1.5em;
  position: relative;
  top: 0.45em;
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
  '''Icon pictogram, hover to see the word.'''
  return ['span.pictogram',
          ['img', {'alt': groups[0], 'src': groups[1] or f'/img/pictogram/{groups[0]}.png'}],
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
          ['a.anchor', {'id':  re.sub(r'[^A-Za-z0-9 ]', '', groups[1]).strip().replace(' ', '-').lower()},
           groups[1].lstrip()]]

StandardInline = Registry(Bold, Underline, Superscript, Subscript, Italic, Stacked, TagBasic, TagAttributes,
                          Monospace, Classed, Strikethrough, MithrilLink, Link,
                          InlineImage, FullImage, Pictogram, Tooltip, Header)

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

@block(Nesting.SUB)
def Aside(text: str):
  r = Paragraphs(text)
  r[0] = 'aside'
  return r

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
  ```
  ---list
  as;fkjasdf
    as;dkfjas
  a sfa sfas;fkj sdf
    as;dkfljas
    asfjas;kdfj
      asdlfjasldfkj
  ...
  ```
  ###Params
  `text`: body text of the list
  `o`: whether list is ordered, in which case an `ol` is returned instead of a `ul`.
  """
  if text is None or text.strip() == '': return ['ol' if o else 'ul']
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
      if pos[-1] != p: pos.append(p)
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
# grid - css grid is a new spec, and there are various possible text representations of it.

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
  Table mode is more flexible. Blank lines are ignored. 
  """
  return t.pipe(text.split('\n'),
                tc.filter(lambda x: x.strip() != ''),
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

@asset_inline(AssetType.CSS, '''
.slideshow{width:100%;position:relative;text-align:center}
.slideshow--item{width:100%;line-height:1.5;display:none}
.slideshow--item img{width:100%;display:inherit}
.slideshow--item::after{content:attr(data-pos);position:absolute;color:white;top:0.25em;right:0.5em;text-anchor:end;padding:0.1em;}
.slideshow--bullet:checked + .slideshow--item{display:block}
.slideshow[data-transition="fade"] .slideshow--item{opacity:0;transition:0.3s ease-out opacity}
.slideshow[data-transition="fade"] .slideshow--bullet:checked + .slideshow--item{opacity:1}
.slideshow--nav{position:absolute;top:0;bottom:0;width:50%;display:none;z-index:88;cursor:pointer;color:transparent;-webkit-touch-callout:none;-webkit-user-select:none;-khtml-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none}
.slideshow--nav:after{display:block;content:'\25B6';font-size:2em;color:#fff;position:absolute;top:50%;right:10px;margin-top:-.5em}
.slideshow--nav-previous{left:0;display:block}
.slideshow--nav-previous:after{transform:scaleX(-1);right:auto;left:10px}
.slideshow--nav-next{left:50%;display:block}
.slideshow--bullet{display:none}
.slideshow--caption {width: 100%;color: white;background: #000a;padding: 0.25em 0;}
''')
@terminal_block()
def Slideshow(text):
  '''
  Shows an image with arrows to go to next/previous images.
  
  ---image-slider
  url1::caption1
  url2::caption2
  ...
  
  Will make an image slider with those images in that order.
  '''
  lines = list(filter(lambda x: x.strip() != "", text.split('\n')))
  name = f'ss-{int(datetime.now().timestamp())}-{re.sub(r"[^a-z]", "", lines[0])}'
  return ['div.slideshow', {'data-transition': 'fade'}, *[
    [['input.slideshow--bullet',
      {'type': 'radio', 'name': name, 'id': f'{name}-item-{i}', 'checked': i == 0}],
     ['div.slideshow--item', {'data-pos': f"{i+1}/{len(lines)}"},
      ['img', {'src': line.split('::')[0]}],
      ['div.slideshow--caption',  t.get(1, line.split('::'), '')],
      ['label.slideshow--nav.slideshow--nav-previous', {'for': f'{name}-item-{(i-1)%len(lines)}'}, f'Go to slide {(i-1)%len(lines) + 1}'],
      ['label.slideshow--nav.slideshow--nav-next', {'for': f'{name}-item-{(i+1)%len(lines)}'}, f'Go to slide {(i+1)%len(lines) + 1}']
    ]
    ] for (i, line) in enumerate(lines)]]

@block()
def Figure(text):
  split = text.split('\n\n', maxsplit=1)
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

@asset_inline(AssetType.CSS, '''
.video {
	position:relative;
	padding-bottom:56.25%;
	padding-top:30px;
	height:0;
	overflow:hidden;
}

.video iframe, .video object, .video embed {
	position:absolute;
	top:0;
	left:0;
	width:100%;
	height:100%;
}
''')
@terminal_block()
def Youtube(url):
  '''
  ---youtube
  http://youtube.com/something
  ...
  
  Creates an iframe with an embedded youtube video that expands to take the
  full width.
  '''
  return ['div.video', ['iframe', {
    'src':url,
    "frameborder":"0",
    "allow":"encrypted-media; picture-in-picture",
    "allowfullscreen":True}]]

@terminal_block()
def Video(url):
  return ['video', {'controls': True},
    ['source', {'src': url}],
    'Your browser does not support the video tag.']

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

@asset_inline(AssetType.CSS, '''
.pdfobject-container {height: 30rem; border: 1rem solid rgba(0,0,0,.1)}
''')
@asset_url(AssetType.JS, 'https://cdnjs.cloudflare.com/ajax/libs/pdfobject/2.1.1/pdfobject.min.js')
@standalone_integration()
def PdfObject(text, docid, elem):
  return f"PDFObject.embed('{text.strip()}', {elem});"


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
  return ['pre', ['code#{0}.language-{1}'.format(h, language), {'key': h+'-element'}, text],
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
  return ['AnnotatedCode', {'code': code.rstrip('\n'), 'annotations': annotations, 'language': language}]

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

@terminal_block()
def LiveYamlComponentDangerous(text, name):
    """
    You can specify your props using the YAML syntax, and create a component in a
    js view library out of it. `name` must be camel case, and upper case, for it to be
    recognized properly by this library.

    :param text: The YAML formatted props to the component
    :param name: name of the component like `AnnotatedCode`
    :return: [name, props] -> syntax that represents this component with these props.
    """
    props = yaml.safe_load(text)
    return ['ℂ'+name, props]

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
  return repr("chordMaker()({0}, {1})".format(elem, repr(info or {})))[1:-1]

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

Standard = Registry(Paragraphs, top=Paragraphs) | StandardInline | CriticMarkup + [
  Aside, Blockquote, List, CodeBySide, SideBySide, Matrix, Katex,
  Slideshow, Figure, Audio, Youtube, Video, PdfObject,
  MusicalAbc, GuitarChord, Code, AnnotatedCode, JsonComponent, YamlComponent,
  LiveYamlComponentDangerous
]
Markdown = Registry(Paragraphs, top=Paragraphs) | MarkdownInline | CriticMarkup
