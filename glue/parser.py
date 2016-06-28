#!/usr/bin/env python3

import operator as op
from typing import Union

import toolz as t
import toolz.curried as tc

from glue.elements import Inline, Block, Nesting, Display
from glue.html import render
from glue.registry import Registry
from glue.util import *

parse = lambda registry, text, topblock=None: parseblock(registry, topblock or registry.top, text)
tohtml = t.compose(render, parse)

def parseinline(registry:Registry,
                element:Union[Block,Inline,str], text:str, parent=None):
  """
  Parses a block of text for its subscribed inline styles.
  Always returns a list of html elements.
  The return value is the body, and it needs to be spliced into the html
  that's being generated in parseblock
  so:
  ['div', *parseinline(registry, element, text)] is what you would do.
  """
  
  block = registry[element] if isinstance(element, str) else element
  subinline = list(registry.inline_subscriptions(block.subinline, parent))
  
  # a map of regexes to parsing function
  inlines = t.pipe(subinline,
    tc.map(lambda x: t.map(lambda p: (p[0],(p[1],x)), x.parser)),
    t.merge,
    lambda x: list(x.items()))
  
  # combine all escaped characters from all subscribed inline objects.
  escapes = ''.join(t.reduce(set.union,
    (x.escape for x in subinline), set())).replace('[', '\\[').replace(']', '\\]')
  # function that will unescape body code so eg \* -> *
  unescape = ((lambda t: re.compile('\\\\(['+escapes+'])').sub(r'\1', t))
              if len(escapes) > 0
              else t.identity)

  # if there are no inline styles declared in the registry, then we need
  # to handle that as a special case before all the regex stuff.
  if len(inlines) == 0:
    return [text]
  
  # combine all inline patterns into one regex.
  # might not be efficient for very complex parsers....
  patt = re.compile('|'.join(t.map(lambda x: '(?:'+x[0].pattern+')', inlines)), re.V1 | re.S | re.M)
  # how many groups are in each regex, in order, so we can assign the final
  # match to the right parser function.
  grouplengths = list(
    t.cons(0, t.accumulate(op.add, t.map(lambda x: num_groups(x[0]), inlines))))

  ind = 0
  l = []
  while ind < len(text):
    m = patt.search(text, ind)
    if m == None:
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
      l.append((elem, parser(parseinline(registry, block, groups[0]))))
    elif elem.nest == Nesting.NONE:
      l.append((elem, parser(groups)))
    elif elem.nest == Nesting.POST:
      # post requires a tree-traversal to reparse all the body elements.
      # the only difference is that we have to
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


def parseblock(registry:Registry,
               block:Block, text:str, parent=None):
  """
  parses text at the block level. ASSUMES VALIDATED REGISTRY.
  minus some minor helper things (defining appropriate )
  """

  def postparseinline(block, text, meta=False):
    html = parseinline(registry, block, text)
    if meta: return html
    else: return [e if isinstance(e, str) else e[1] for e in html]

  def postparse(block, text, meta=False):
    subblocks = list(splitblocks(text))
    if len(subblocks) == 1 and isinstance(subblocks[0], str):
      # there are no subblocks, so return one level up!
      return postparseinline(block, subblocks[0], meta)
      
    l = []
    for b in subblocks:
      if isinstance(b, list):
        sub = parseblock(registry, registry[b[0]], b[1])
        if meta:
          l.append((registry[b[0]], sub))
        else:
          l.append(sub)
      elif isinstance(b, str):
        l += postparseinline(block, b, meta)

    return l
  
  if block.nest == Nesting.NONE:
    # separate pathway, we just parse the block
    return block.parser(text)
  
  if block.nest == Nesting.POST:
    # parse block first, then call parseblock on the children.
    return splicehtmlmap(t.partial(postparse, block), block.parser(text))
  
  if block.nest == Nesting.SUB:
    blocks = postparse(block, text, meta=True)
    print(blocks)
    # make sub directory, and string only array:
    subtext = []
    subs = {}
    i = 1
    for e in blocks:
      if isinstance(e, str):
        subtext.append(e)
      elif isinstance(e, tuple):
        substr = ('[|{}|]' if isinstance(e[0], Inline) and e[0].display is Display.INLINE else '[||{}||]').format(i)
        subs[substr] = e[1]
        subtext.append(substr)
        i += 1

    return splicehtmlmap(
      lambda text: [subs[x] if x.startswith('[|') and x.endswith('|]') else x
                 for x in re.split(r'(\[\|\|?\d+\|?\|\])', text) if x != ''],
      block.parser(''.join(subtext)))
