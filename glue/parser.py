#!/usr/bin/env python3

from typing import List, Callable, Mapping, Union

import operator as op
import toolz as t
import toolz.curried as tc
import regex as re

from glue.registry import Registry
from glue.util import *
from glue.elements import Inline, Block, Nesting
from glue.html import render

def parse(registry, topblock, text):
  return render(parseblock(registry, topblock, text))


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
    (x.escape for x in subinline))).replace('[', '\\[').replace(']', '\\]')
  # function that will unescape body code so eg \* -> *
  unescape = lambda t: re.compile('\\\\(['+escapes+'])').sub(r'\1', t)
  
  # combine all inline patterns into one regex.
  # might not be efficient for very complex parsers....
  patt = re.compile('|'.join(t.map(lambda x: '(?:'+x[0].pattern+')', inlines)), re.V1)
  # how many groups are in each regex, in order, so we can assign the final
  # match to the right parser function.
  grouplengths = list(
    t.cons(0, t.accumulate(op.add, t.map(lambda x: num_groups(x[0]), inlines))))

  ind = 0
  l = []
  while ind < len(text):
    m = patt.search(text, ind)
    print(m)
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
    if elem.nest == Nesting.FRAME:
      # frames are simple, by default they have inherit behavior
      # and deal with one group
      l.append(parser(parseinline(registry, block, groups[0])))
    elif elem.nest == Nesting.POST:
      # post requires a tree-traversal to reparse all the body elements.
      # the only difference is that we have to
      l.append(list(
        splicehtmlmap(
          lambda t: parseinline(
            registry,
            block if elem.subinline == ['inherit'] else elem,
            t,
            parent if elem.subinline == ['inherit'] else block),
          parser(groups))))
    elif elem.nest == Nesting.NONE:
      l.append(parser(groups))

    ind = m.span()[1]
  
  return l


def parseblock(registry:Registry,
               block:Block, text:str, parent=None):
  """
  parses text at the block level. ASSUMES VALIDATED REGISTRY.
  minus some minor helper things (defining appropriate )
  """
  def postparse(block, text):
    subblocks = list(splitblocks(text))
    if len(subblocks) == 1:
      # there are no subblocks, so return one level up!
      return parseinline(registry, block, subblocks[0])
      
    l = []
    for b in subblocks:
      if isinstance(b, list):
        l.append(parseblock(registry, registry[b[0]], b[1]))
      elif isinstance(b, str):
        t = parseinline(registry, block, b)
        if isinstance(t,str):
          l.append(t)
        else:
          l += t

    return l
  
  if block.nest == Nesting.NONE:
    # separate pathway, we just parse inline styles and then parse the block
    return block.parser(parseinline(registry, block, text))
  
  if block.nest == Nesting.POST:
          
    # parse block first, then call parseblock on the children.
    return splicehtmlmap(t.partial(postparse, block), block.parser(text))
  
  if block.nest == Nesting.SUB:
    blocks = postparse(block, text)
    # make sub directory, and string only array:
    subtext = []
    subs = {}
    i = 1
    for e in blocks:
      if isinstance(e, (list, tuple)):
        substr = '[|{}|]'.format(i)
        subs[substr] = e
        subtext.append(substr)
        i += 1
      else:
        subtext.append(e)
    
    return splicehtmlmap(
      lambda t: [subs[x] if x.startswith('[|') else x
                 for x in re.split(r'(\[\|\d+\|\])', t)],
      block.parser(''.join(subtext)))
