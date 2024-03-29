import abc
import enum
import copy
import uuid
from enum import Enum
from typing import Mapping, Union, Set, Callable

import functools
import inflection
import regex as re

# --------------------- ELEMENT UTILITIES ---------------------------------
from glue import css


def makename(name: str) -> str:
  """Turns a capital camelcase name into a dasherized name for block detection.
  Used as the logic for autogenerating the `name` attribute of an `Element`.
  """
  return inflection.dasherize(inflection.underscore(name))


@enum.unique
class Patterns(Enum):
  """
  Defines some known regex pattern templates for common types of inline syntax.
  For example, a single group inline element (one capture group framed by
  something before and after the group).

  Note: `(?<!\\)(?:\\\\)*` is a syntax for detecting an odd number of \ characters.
  This is used prior to the start of some pattern element so that the pattern can be escaped 
  in case the user wnats the literal value of that character. 
  """
  escape = r'(?<!\\)(?:\\\\)*{0}'
  single_group = r'(?<!\\)(?:\\\\)*\K{0}(.*?(?<!\\)(?:\\\\)*){1}'
  link = r'(?<!\\)(?:\\\\)*\K{0}\[((?:(?:[^\[])|(?:\[.*?\]))*?(?<!\\)(?:\\\\)*)\]\(((?:\([^\)]*\)|[^)\n])*)\)'
  double_group = r'(?<!\\)(?:\\\\)*\K\{0}(.*?(?<!\\)(?:\\\\)*){1}(.*?(?<!\\)(?:\\\\)*){2}'
  # matches structures like <ident.class.class2:text> useful for one line html tag formats.
  tag_simple = r'(?<!\\)(?:\\\\)*\K<([a-zA-Z][a-zA-Z0-9_-]*)((?:\.[a-zA-Z][a-zA-Z0-9_-]*)*):\s*([^>]+)>'
  tag_attributes = r'(?<!\\)(?:\\\\)*\K<([a-zA-Z][a-zA-Z0-9_-]*)((?:\.[a-zA-Z][a-zA-Z0-9_-]*)*)(?:\s+([a-zA-Z]+)=("[^"]+"))+:\s*([^>]+)>'

Nesting = Enum('Nesting', 'FRAME POST SUB NONE')
Nesting.__doc__ = """
FRAME: element is intended to contain/frame the inside
       text, which means that subscriptions should be inherited from the parent.

POST: text in the block should be parsed AFTER this block is
      parsed. This is the default, and is suitable for most situations.

SUB: the inside of the text is parsed for child nodes (inline and
     block) first, and the corresponding sections are replaced with [|*|] style
     tags that are meant to be left UNTOUCHED. After this block is parsed,
     then the tags are replaced with the appropriate parsed sections. This could
     have also been called 'PRE', since it pre-parses the contents before
     calling the block's parsing function.

NONE: terminal element. The parser's output is taken verbatim, with out any
      further processing of its insides.
"""

Display = Enum('Display', 'BLOCK INLINE')
Display.__doc__ = """
You can set an inline element to be displayed like a block element. This is
good for things like header elements in markdown syntax, which are detected by
regex, but are not intended to be wrapped in any other kind of block.

INLINE: should be displayed like a HTML inline (think span) (default)

BLOCK: should be displayed like a HTML block (think div)
"""


AssetType = Enum('AssetType', 'JS CSS')
AssetType.__doc__ = """
There are at least two kinds of assets - the ones that are scripts
(eg, `<script src="blah blah"></script>`), and the ones that are CSS
(eg `<link rel="stylesheet" type="text/css" href="blah blah"/>`).

Accordingly there are two values for this Enum so far:

JS: something written in the JS language
CSS: a stylesheet written in CSS
SCSS: a stylesheet written in SCSS, preprocessed through libsass.
"""
# ------------------  BASE ELEMENTS --------------------------


class Element(abc.ABC):
  """
  Base class for all elements, which itself is really just a parser function
  augmented with some necessary data to plug into the glue system.

  There are four instance variables:

  `nest` is the nesting policy. It controls in which order the sub-blocks/inline
  elements are parsed. See the `Nesting` enum for more information on what the
  kinds of nesting policies are and how they are expected to function.

  `sub` is a list of the subscriptions this element is maintinaing. Only the
  elements appearing in this list can be sub blocks or inline elements of this
  element. There are two special keywords. The first is `'all'` which means all
  elements in the registry are fair game. The second is `'inherit'` which means
  that this block allows exactly what its parent allows through. `'inherit'` is
  a rare choice, and most blocks will just have `'all'` as their subscription
  policy.

  `parser` is a function that is supposed to take the body of the block along
  with any options (or just the captured groups of an inline element) and
  generate HTML output (in the cottonmouth list form). It has slightly different
  semantics for each of the subclasses, and different signatures as well
  depending on what they are parsing and how.

  `assets` is a set of strings each of which is a valid HTML tag (plus contents)
  that adds an asset such as a script (JS) or stylesheet (CSS) to the page.
  It is recommended that you use the helpers to construct these, rather than
  go through the tedious process of trying to write it out yourself.

  An additional property is:

  `name` is the name of the element. The name has two uses - it becomes the key
  for the element in the registry, and it also is the 'dispatch' (think like a
  function call) for the block. The name is auto-generated for the sake of
  sanity by taking a camelcase name (which is consistent with python naming style)
  and converting it into something dash-separated so that it's easier to type
  into the editor.

  ```
  ---block
  blah blah blah
  ...
  ```

  after the `---` the name is used to dispatch to the appropriate block element,
  whose parser function will be called to parse the contents of that block.
  For the sake of sanity, the name is autogenerated based on the class name.
  """


  # this class does not require instance data, so we can save space.
  #__slots__ = ()

  def __eq__(self, other):
    for attr in self.__dict__:
      if getattr(self, attr) != getattr(other, attr):
        return False
    return True

  def __repr__(self):
    return f'{self.__class__.__name__}(name={inflection.camelize(inflection.underscore(self.name))})'

  def __hash__(self):
    return self.name.__hash__()

  def __init__(self, parser: Callable, nest: Nesting, sub: ['Element']):
    self.nest = nest
    self.sub = sub
    self.parser = parser
    self.name = makename(self.parser.__name__)
    self.assets = []

  def __call__(self, *args, **kwargs):
    return self.parser(*args, **kwargs)

  def _replace(self, **kwargs):
    copied = copy.copy(self)
    for k in kwargs:
      if hasattr(copied, k):
        setattr(copied, k, kwargs[k])
    return copied

  def validate(self) -> bool:
    # If there's no nesting there should be no subscriptions
    if self.nest == Nesting.NONE and self.sub != []: return False
    # Frames should not restrict what can be put inside them, since they
    # don't process anything inside themselves.
    if self.nest == Nesting.FRAME and self.sub != ['inherit']: return False
    return True

  def add_asset(self, asset: str):
    self.assets.append(asset.strip())


class Block(Element):
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

  `sub` is an array of literal elements that this block
  accepts as sub-blocks. In general, most blocks will either be `Nesting.NONE` or
  accept every block, but you can be more specific if you'd like.

  `subinline` is the same, but restricted to `Inline` elements. It's generated
  from the sub list, and it's existence is just an optimization to avoid having
  to do the filter ecah time.

  `parser` is a function that takes string text and outputs html corresponding
  to whatever this block would like to parse.

  `opts` is a string passed to getopts that states which flags are allowed
  as kwargs options for this block.
  """
  def __init__(self, parser: Callable, nest: Nesting, sub: [Element],
               opts: str):
    super(Block, self).__init__(parser, nest, sub)
    self.opts = opts
    self.subinline = [x for x in sub
                      if x == 'all' or x == 'inherit' or isinstance(x, Inline)]


class Inline(Element):
  """
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

  `sub` is a list of literal element objects that define
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

  `display` is a switch that allows inline elements to be displayed as blocks
  (eg, with no other elements like div/section/p wrapping them). A good example
  of when Display.BLOCK is a good idea is for Markdown style headers.
  Note that the regex for a Display.BLOCK type case is limited to exist on ONLY
  one line. This is a necessary restriction to not conflict with the multiline
  regex being used to split blocks. Please use Display.BLOCK sparingly.
  """
  def __init__(self, regex,
                     parser: Callable,
                     nest: Nesting = Nesting.FRAME,
                     sub: ['Inline'] = None,
                     escape: str = '',
                     display: Display = Display.INLINE):
    super(Inline, self).__init__(parser, nest, sub or ['all'])
    self.regex = re.compile(regex) if isinstance(regex, str) else regex
    self.escape = escape
    self.display = display
    self.subinline = [x for x in (sub or ['all'])
                      if x == 'all' or x == 'inherit' or isinstance(x, Inline)]

  def validate(self):
    super(Inline, self).validate()
    if self.display == Display.BLOCK and not (
          self.regex.pattern.startswith('^') and self.regex.pattern.endswith('$')):
      return False
    return True

# ---------------------- ASSET CONSTRUCTOR UTILITIES -------------------------

def asset_url(type: AssetType, url: str):
  def asset_url_helper(elem: Element):
    elem.add_asset('<script src="{0}"></script>'.format(url)
                   if type == AssetType.JS
                   else '<link rel="stylesheet" href="{0}"/>'.format(url))
    return elem
  return asset_url_helper

def asset_inline(type: AssetType, contents: Union[str, list]):
  def asset_inline_helper(elem: Element):
    elem.add_asset('<script defer type="text/javascript">\n{0}\n</script>'.format(contents)
                   if type == AssetType.JS
                   else '<style>\n{0}\n</style>'.format(css.scss(contents)
                                                        if isinstance(contents, list)
                                                        else contents))
    return elem
  return asset_inline_helper

# ----------------------- ELEMENT CONSTRUCTOR UTILITIES ----------------------

def block(nest=Nesting.POST, sub=None, opts=''):
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
  def block_fn(parser:Callable) -> Block:
    return Block(parser, nest, sub or ['all'], opts)

  return block_fn

def terminal_block(opts=''):
  """
  Decorator for blocks that have nesting = NONE and do not subscribe to any
  inline or block elements. Note that NONE type blocks should NOT subscribe
  to any such elements, anyway, so it is convenient to use this function.
  :param opts: see Block documentation.
  :return: a decorator that converts a parser function to a Block object of the
  same name. See Block for details.
  """
  return block(Nesting.NONE, [], opts)

def standalone_integration(outer_elem='div', inner_elem='div'):
  """
  Decorator that takes a function with signature `(text: str, docid: str, elem: str) -> str` that spits out the
  script contents required to inject the integrated content into the element, and generates a block that wraps that
  logic. That's kinda confusing - see examples like `Katex` or `MusicalAbc` in the library.py file.
  
  :param outer_elem: optional if you want something other than a `div` on the outside
  :param inner_elem: optional if you want something other than a `div` on the inside (eg, `svg`, `pre`, etc).
  :return: a `Block` that generates HTML to inject content into the site integrated with a JS library.
  """
  def standalone_integration_wrapper(f):
    @terminal_block()
    @functools.wraps(f)
    def standalone_block(text):
      docid = makename(f.__name__) + '-' + str(uuid.uuid4())
      elem = "document.getElementById('{0}')".format(docid)

      return [outer_elem + '.' + makename(f.__name__),
              [inner_elem + '#{0}'.format(docid), {'key': docid+"-container"}],
              ['script', {'key': docid}, f(text, docid=docid, elem=elem)]]
    return standalone_block

  return standalone_integration_wrapper


def inline(regex, nest=Nesting.FRAME, sub=None, escape='', display=Display.INLINE):
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
  def inline_fn(parser:Callable) -> Inline:
    return Inline(regex, parser, nest, sub, escape, display)

  return inline_fn

def inline_one(start: str, end: str, nest=Nesting.FRAME, sub=None, display=Display.INLINE):
  """
  """
  patt = re.compile(Patterns.single_group.value.format(
    re.escape(start), re.escape(end)))
  return inline(patt, escape=[start[0], end[0]],
                nest=nest, display=display, sub=sub)
  
def SingleGroupInline(name: str, start: str, end: str, tag: str,
                      attr: Mapping[str, str]=None):
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
  parser = lambda body: [tag, attr or {}, body]
  parser.__name__ = name
  return inline_one(start, end)(parser)

def IdenticalInline(name: str, s:str, tag:str, attr:Mapping[str, str]=None):
  """
  A very simple wrapper around `SingleGroupInlineFrame` that will work
  if you expect the start/end of the element to be the same. Eg: `*bold*`.
  """
  return SingleGroupInline(name, s, s, tag, attr)

def MirrorInline(name:str, start:str, tag:str, attr:Mapping[str, str]=None):
  """
  A very simple wrapper around `SingleGroupInlineFrame` that is for when
  the start/end of the element are mirrors of each other, eg: `{++add++}`
  Handles ()[]{}<> flipping.
  """
  return SingleGroupInline(
    name, start,
    start[::-1].translate(str.maketrans('()[]{}<>', ')(][}{><')),
    tag, attr)

def link(designation: str, nest=Nesting.POST, sub=None):
  """
  Convenience decorator for two-group inline elements that look like markdown links.
  In other words, we expect `something[group1](group2)`. The pattern is limited to
  using square/round parens in that exact way.

  :param designation: the string that goes in front of the link. Eg, a tooltip
  might have the syntax `T[text](tooltip text)`, so the designation would be `'T'`
  :return: a new Inline element with the syntax of designation + [group1](group2)
  that is parsed by the parser that this decorator is going to wrap.
  """
  pattern = re.compile(Patterns.link.value.format(designation), re.V1)
  def link_fn(parser :Callable):
    return Inline(pattern, parser, nest, sub or ['inherit'],
                  escape='()[]'+ designation[0] if len(designation) > 0 else '')

  return link_fn

def inline_two(start: str, mid: str, end: str, nest=Nesting.POST, sub=None):
  """

  :param start: what goes at the beginning of the pattern, eg `{~~`
  :param mid: what goes in between the two capture groups, eg `~>`
  :param end: what goes at the end of the second capture group eg `~~}`
  :param nest: see Inline/Nesting for description of Nesting policies
  :param sub: subscription list (see Inline#sub)
  :return:
  """
  pattern = re.compile(Patterns.double_group.value.format(start, mid, end), re.V1)
  def inline_two_fn(parser: Callable):
    return Inline(pattern, parser, nest, sub or ['inherit'])

  return inline_two_fn

# ------------------------ OTHER UTILITIES ------------------------

def wrap(e: Element):
  """
  Creates a new Element by wrapping the parser function of another Element.

  >>> wrap('NewBlock', lambda x: x)(SomeBlock)
  Block(name='NewBlock', ...)
  """
  def wrapper(f: Callable):
    @functools.wraps(e.parser)
    def new_parser(*args, **kwargs):
      return f(e.parser(*args, **kwargs))
    
    new_element = copy.copy(e)
    new_element.parser = new_parser
    new_element.name = makename(f.__name__)
    return new_element
  return wrapper 
