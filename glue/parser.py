#!/usr/bin/env python3

from typing import Mapping
import operator as op
from getopt import getopt
from typing import Union

from glue.elements import Element, Inline, Block, Nesting, Display
from glue.html import render
from glue.registry import Registry
from glue.util import *

# This module contains all the functions that parse an input text string and
# return HTML corresponding to the page that is generated.

def parseinline(registry:Registry,
                element:Union[Element,str], text:str, parent=None):
  """
  Parses a block of text for its subscribed inline styles.
  Always returns a list of html elements.
  The return value is the body, and it needs to be spliced into the html
  that's being generated in parseblock
  so:
  ['div', *parseinline(registry, element, text)] is what you would do.
  """
  if text == '': return ['']

  block = registry[element] if isinstance(element, str) else element
  subinline = list(registry.inline_subscriptions(block.subinline, parent))

  # a map of regexes to parsing function
  inlines = [(x.regex, (x.parser, x)) for x in subinline]

  # combine all escaped characters from all subscribed inline objects.
  escapes = ''.join(t.reduce(set.union,
    (x.escape for x in subinline), set())).replace('[', '\\[').replace(']', '\\]')
  # function that will unescape body code so eg `\\\*` -> `\*`
  unescape = ((lambda t: re.compile('\\\\(['+re.escape(escapes)+'])').sub(r'\1', t))
              if len(escapes) > 0
              else t.identity)

  # if there are no inline styles declared in the registry, then we need
  # to handle that as a special case before all the regex stuff.
  if len(inlines) == 0:
    return [text]
  
  # combine all inline patterns into one regex.
  # might not be efficient for very complex parsers....
  patt = re.compile('|'.join(t.map(lambda x: '(?:'+(
    x[0] if isinstance(x[0], str) else x[0].pattern)+')', inlines)), re.V1 | re.S | re.M)

  # how many groups are in each regex, in order, so we can assign the final
  # match to the right parser function.
  grouplengths = list(
    t.cons(0, t.accumulate(op.add, t.map(lambda x: num_groups(x[0]), inlines))))

  ind = 0
  l = []
  while ind < len(text):
    m = patt.search(text, ind)
    if m is None:
      l.append(unescape(text[ind:]))
      break

    # untouched text should be made into its own child
    if m.span()[0] > ind:
      l.append(unescape(text[ind:m.span()[0]]))
    
    # figure out which parser the match is corresponding to.
    # first not-None group index.
    groupind = indexby(lambda x: x is not None, m.groups())
    # the index of the regex in `inlines` that the groupind corresponds to
    matchind = indexby(lambda x: x >= groupind, grouplengths)
    parser, elem = inlines[matchind][1]
    # stripping all the groups corresponding to the matched sub-regex
    groups = m.groups()[grouplengths[matchind]:
                        grouplengths[min(m.re.groups, matchind+1)]]

    # doing the parsing based on nesting type
    if elem.nest == Nesting.FRAME:
      # frames are simple, by default they have inherit behavior
      # and deal with one group
      l.append((elem, list(splicehtmlmap(lambda t: parseinline(
        registry, block, t, parent), parser(groups[0]) )) ) )
    elif elem.nest == Nesting.NONE:
      l.append((elem, parser(groups)))
    elif elem.nest == Nesting.POST:
      # post requires a tree-traversal to reparse all the body elements.
      # the only difference is that we have to take into account the inheritance
      # rules.
      l.append((elem, list(
        splicehtmlmap(
          lambda t: parseinline(
            registry,
            block if elem.subinline == ['inherit'] else elem,
            t,
            parent if elem.subinline == ['inherit'] else block),
          parser(groups)))))

    ind = m.span()[1]

  return l


def parseblock(registry:Registry, block:Block, text:str, args=None, parent=None):
  """parses text at the block level. ASSUMES VALIDATED REGISTRY."""
  # handle default args
  if args is None:
    kwopts = {}
    opts = []
  else:
    kw, opts = getopt(args, block.opts)
    kwopts = dict((e[0].lstrip('-'), True if e[1] == '' else e[1]) for e in kw)


  def postparseinline(block, text, meta=False):
    html = parseinline(registry, block, text)
    if meta is False: return map(unpack, html)
    return html

  def postparse(block, text, meta=False):
    subblocks = list(splitblocks(text))
    if len(subblocks) == 1 and isinstance(subblocks[0], str):
      # there are no subblocks, so return one level up!
      return postparseinline(block, subblocks[0], meta)
      
    l = []
    for b in subblocks:
      if isinstance(b, list):
        blockname, *classnames = b[0].split('.')
        if blockname not in registry:  # means block name is not in registry
          raise ValueError('Parser Error: Block `{}` is not in registry'.format(b[0]))
        sub = parseblock(registry, registry[blockname], b[2], args=b[1])
        if len(classnames) > 0:
          # have to incur this cost otherwise will not be able to append 
          # the classnames. There is a pure generator version of this 
          # that I could write, but not interested in debugging that right now. 
          sub = unwind(sub)
          sub[0] += f'.{".".join(classnames)}'
        if meta:
          l.append((registry[blockname], sub))
        else:
          l.append(sub)
      elif isinstance(b, str):
        l += postparseinline(block, b, meta)

    return l
  
  if block.nest == Nesting.NONE:
    # separate pathway, we just parse the block
    return block.parser(text, *opts, **kwopts)
  
  elif block.nest == Nesting.POST:
    # parse block first, then call parseblock on the children.
    return splicehtmlmap(t.partial(postparse, block), block.parser(text, *opts, **kwopts))
  
  elif block.nest == Nesting.SUB:
    blocks = postparse(block, text, meta=True)
    # make sub directory, and string only array:
    subtext = []
    subs = {}
    i = 1
    for e in blocks:
      if isinstance(e, str):
        subtext.append(e)
      elif isinstance(e, (list, tuple)):
        substr = ('[|{}|]' if isinstance(e[0], Inline) and e[0].display is Display.INLINE else '[||{}||]').format(i)
        subs[substr] = unpack(e[1])
        subtext.append(substr)
        i += 1
    return splicehtmlmap(
      lambda text: [subs[x] if x.startswith('[|') and x.endswith('|]') else x
                 for x in re.split(r'(\[\|\|?\d+\|?\|\])', text) if x != ''],
      block.parser(''.join(subtext), *opts, **kwopts))


def parse(registry: Registry, text: str, topblock:Block=None):
  """Parse input text with the known blocks/inline elements in registry.
  All config parameters are pretty much setup inside registry, although you can
  force `parse` to use a different block as the top context block if you wish.

  :param registry: the `Registry` object available
  :param text: the text you want to parse into HTML
  :param topblock: Block (in the registry) that is considered the outermost context of the text.
  :return: list-style html.
  """
  return parseblock(registry, topblock or registry.top, text)


macro_pattern = re.compile(r'(?<!\\)(?:\\\\)*\K\$\{([\w-\.]+)\}')
def macroexpand1(macros: Mapping[str, str], s: str):
  """
  `macroexpand1` takes the variable and expands all macros in it ONE time.
  :param macros: mapping of macro name to output, which can include more macros.
  :param s: the text that needs to be expanded.
  :return: a new string with one level of expanding done.
  """
  expanded = ''
  i = 0
  for m in re.finditer(macro_pattern, s):
    expanded += s[i:m.start()] + macros[m.group(1)]
    i = m.end()
  expanded += s[i:len(s)]

  if expanded == '': return s
  return expanded

def macroexpand(macros: Mapping[str, str], s:str):
  """
  Does `macroexpand1` until there are no more macros left to expand.
  :param macros: mapping of macro name to output, which can include more macros.
  :param s: the text that needs to be expanded.
  :return: completely expanded string.
  """

  expanded = s
  next = macroexpand1(macros, expanded)
  while expanded != next:
    expanded = next
    next = macroexpand1(macros, expanded)

  return expanded

def parsemacros(s: str):
  return map(lambda x: [y.strip() for y in x.split('=', maxsplit=1)], s.split('\n'))
