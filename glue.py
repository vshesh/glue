# for js: https://github.com/davidchambers/string-format

from typing import List, Callable, Mapping, Union

from collections import namedtuple as nt
from enum import Enum
import operator as op

import toolz as t
import toolz.curried as tc
import regex as re

Nesting = Enum('Nesting', 'FRAME POST SUB NONE')

Block = nt('Block', ['name', 'nestb', 'nesti', 'subblock', 'subinline', 'parser'])
Block.__call__ = lambda self, *args, **kwargs: self.parser(*args, **kwargs)

Inline = nt('Inline', ['name', 'nest', 'subscribe', 'escape', 'parser'])


def htmlbodymap(f, x):
  if isinstance(x, list) or isinstance(x, tuple):
    return list(t.cons(x[0], t.map(lambda e: htmlbodymap(f,e), x[1:])))
  elif isinstance(x, str):
    return f(x)
  else:
    return x

cut = lambda i,s: (s[:i], s[i:])

def stringcat(*s:str):
  for string in s:
    for c in string:
      yield c

def num_groups(regex):
  return re.compile(regex).groups

def indexby(f, lst):
  return next(i for i, j in enumerate(lst) if f(j))

def fills(quantities, n):
  """
  fillto([1,1,1],1) => 1
  let's say you have ordered buckets, each with quantity q_i.
  `quantities = [q_1, q_2...q_k]`.
  Then you have n units of water. How many buckets can you fill?
  That's what this function answers.
  it returns the index of the next empty bucket after using n units of water
  to fill the quantities in the array in a row.
  """
  k = n
  for i,e in enumerate(quantities):
    k -= e
    if k < 0: return i
  
  return len(quantities)


def parseinline(registry:Mapping[str, Union[Inline, Block]],
                element:Union[Block,Inline,str], text:str):
  """
  Parses a block of text for its subscribed inline styles,
  depending on the nesting style of the block, it will return
  """
  
  block = registry[element] if isinstance(element, str) else element
    
  # a map of regexes to parsing function
  inlines = t.pipe(
    block.subinline if isinstance(block, Block) else block.subscribe,
    tc.map(lambda x: x if isinstance(x, Inline) else registry[x]),
    tc.map(lambda x: t.map(lambda p: (p[0],(p[1],x)), x.parser)),
    t.merge,
    lambda x: list(x.items()))
  
  # combine all escaped characters from all subscribed inline objects.
  escapes = ''.join(t.reduce(set.union,
    ((x if isinstance(x, Inline) else registry[x]).escape
     for x in block.subinline))).replace('[', '\\[').replace(']', '\\]')
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
    if m == None:
      if ind == 0: return text
      l.append(unescape(text[ind:]))
      break
    else:
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
        l.append(
          htmlbodymap(
            lambda t: parseinline(
              registry,
              block if elem.subscribe == 'inherit' else elem,
              t),
            parser(groups)))
      else:
        l.append((parser, groups))

      ind = m.span()[1]
  
  return l[0] if len(l) == 1 and isinstance(l[0], list) else l

def splitblocks(text:str):
  return t.map(lambda b: b[3:].split('\n', 1) if b.startswith('---') else b,
               re.split(re.compile(r'\n(---(?:.|\n)*?)\n\.\.\.\n', re.MULTILINE),
                        text))

def parseblock(registry:Mapping[str, Union[Inline, Block]],
               block:Block, text:str, parent:Block=None):
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
        l.append(parseblock(registry, registry[b[0]], b[1], block))
      elif isinstance(b, str):
        t = parseinline(registry, block, b)
        if isinstance(t,str):
          l.append(t)
        else:
          l += t

    return l
  
  if block.nestb == Nesting.NONE:
    # separate pathway, we just parse inline styles and then parse the block
    return block.parser(parseinline(registry, block, text))
  
  if block.nestb == Nesting.POST:
          
    # parse block first, then call parseblock on the children.
    return htmlbodymap(t.partial(postparse, block), block.parser(text))
  
  # if block.nestb == Nesting.FRAME:
  #   return block.parser(postparse(parent or block, ))
  # # if registy[block]['nesting'] == 'sub':
  # # first, extract all sub-blocks in the text.
  # # this needs to be only done at level 1. If the blocks allow nesting, then
  # # the dispatch will call parse AGAIN, which will extract blocks again.
  # subi = 1
  # subblocks = {}
  # l = []
  # for b in block:
  #   if b.startswith('---'):
  #     dispatch, body = b[3:].split('\n', 1)
  #     # for now, dispatch is just a string
  #     kind = dispatch.trim()
  #     subblocks[subi] = parseblock(registry, kind, body)
  #     subi += 1
  #     l.append('{{{}}}'.format(subi))
  #   else:
  #     l.append(b)
  #
  # return l



InlineFrame = lambda name, escape, parser: Inline(
  name, Nesting.FRAME, 'inherit', escape, parser)

def SingleGroupInlineFrame(name:str, start:str, end:str,
                           tag:str, attr:Mapping[str,str]=None):
  patt = re.compile(
    '(?<!\\\\)(?:\\\\\\\\)*\\K{0}(.*?(?<!\\\\)(?:\\\\\\\\)*){1}'.format(
      re.escape(start), re.escape(end)))
  return InlineFrame(name, set(stringcat(start, end)),
    [(patt, lambda body: [tag, attr or {}, body])])

def IdenticalInlineFrame(name:str, s:str, tag:str, attr:Mapping[str,str]=None):
  return SingleGroupInlineFrame(name, s, s, tag, attr)
  
def MirrorInlineFrame(name:str, start:str, tag:str, attr:Mapping[str,str]=None):
  return SingleGroupInlineFrame(
    name, start,
    start[::-1].translate(str.maketrans('()[]{}<>', ')(][}{><')),
    tag, attr)

Bold = IdenticalInlineFrame('bold', '*', 'strong')
Italic = IdenticalInlineFrame('italic', '_', 'em')
Monospace = IdenticalInlineFrame('monospace', '`', 'code')
Underline = IdenticalInlineFrame('underline', '__', 'span',
  {'text-decoration': 'underline'})

CriticAdd = MirrorInlineFrame('critic-add', '{++', 'ins')
CriticDel = MirrorInlineFrame('critic-del', '{--', 'del')
CriticComment = MirrorInlineFrame('critic-comment', '{>>', 'span.critic.comment')
CriticHighlight = MirrorInlineFrame('critic-highlight', '{==', 'mark')

Link = Inline('link', Nesting.POST, 'inherit', '()[]',
  [(re.compile(
    r'(?<!\\)(?:\\\\)*\K\[(.*?(?<!\\)(?:\\\\)*)\]\((.*?(?<!\\)(?:\\\\)*)\)'),
   lambda groups: ['a', {'href': groups[1]}, groups[0]])])

NoopBlock = Block('noop', Nesting.NONE, Nesting.POST, [], [],
  lambda body: ['div', *body])

Paragraphs = Block('paragraphs', Nesting.POST, Nesting.POST, [],
  [Bold, Italic, Monospace, Underline, Link],
  lambda text: list(t.cons('div', t.map(lambda x: ['p', x.strip()], text.split('\n\n')))))

def makeregistry(*args: Union[Block, Inline]):
  return dict((x.name, x) for x in args)

registry = makeregistry(Bold, Italic, Monospace, Underline, Link, NoopBlock, Paragraphs)
