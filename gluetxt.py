# for js: https://github.com/davidchambers/string-format

from typing import List, Callable, Mapping, Union

from collections import namedtuple as nt
from collections import OrderedDict as odict
from enum import Enum
import operator as op

import toolz as t
import toolz.curried as tc
import regex as re



# Paragraphs = Block('paragraphs', 'post', ''
#  lambda text: t.cons('div', t.map(lambda x: ['p', x], text.split('\n\n'))))

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
    if k <0: return i
  
  return len(quantities)

  
def parseinline(registry:Mapping[str, Union[Inline, Block]],
                block:Block, text:str):
  """
  Parses a block of text for its subscribed inline styles,
  depending on the nesting style of the block, it will return
  """
    
  # a map of regexes to parsing function
  inlines = t.pipe(block.subinline,
    tc.map(lambda x: x if isinstance(x, Inline) else registry[x]),
    tc.map(lambda x: t.map(lambda p: (p[0],(p[1],x)), x.parser)),
    t.merge,
    lambda x: list(x.items()))
  
  escapes = ''.join(t.reduce(set.union,
    ((x if isinstance(x, Inline) else registry[x]).escape
     for x in block.subinline)))
  
  unescape = lambda t: re.compile('\\\\(['+escapes+'])').sub(r'\1', t)
  
  patt = re.compile('|'.join(t.map(lambda x: '(?:'+x[0].pattern+')', inlines)), re.V1)
  grouplengths = t.accumulate(op.add, t.map(lambda x: num_groups(x[0]), inlines))

  ind = 0
  l = []
  while ind < len(text):
    m = patt.search(text, ind)
    if m == None:
      l.append(unescape(text[ind:]))
      break
    else:
      if m.span()[0] > ind:
        l.append(unescape(text[ind:m.span()[0]]))
      
      ind = m.span()[1]
      groupind = indexby(lambda x: x is not None, m.groups())
      matchind = indexby(lambda x: x > groupind, grouplengths)
      parser = inlines[matchind][1]
      groups = m.groups()[matchind:min(m.re.groups, matchind+1)]
      if parser[1].nest == Nesting.FRAME:
        l.append(parser[0](parseinline(registry, block, groups[0])))
      else:
        l.append((parser, groups))
  
  return l


def parseblock(registry:Mapping[str, Union[Inline, Block]], block:Block, text:str):
  """
  parses text at the block level. ASSUMES VALIDATED REGISTRY.
  minus some minor helper things (defining appropriate )
  """
  if block.nestb == Nesting.FRAME:
    # separate pathway, we just parse inline styles and then parse the block
    return block.parser() + parseinline(registry, block, text)
    
  # if registy[block]['nesting'] == 'sub':
  #   # first, extract all sub-blocks in the text.
  #   # this needs to be only done at level 1. If the blocks allow nesting, then
  #   # the dispatch will call parse AGAIN, which will extract blocks again.
  #   blocks = re.split(re.compile('\n(---(?:.|\n)*)\n...\n', re.MULTILINE), text)
  #   subi = 1
  #   subblocks = {}
  #   l = []
  #   for b in block:
  #     if b.startswith('---'):
  #       dispatch, body = b[3:].split('\n', 1)
  #       # for now, dispatch is just a string
  #       kind = dispatch.trim()
  #       subblocks[subi] = parseblock(registry, kind, body)
  #       subi += 1
  #       l.append('{{{}}}'.format(subi))
  #     else:
  #       l.append(b)
  #
  #   bodyformat(registry[block]['parser'](join(l)), subblocks)
    


Nesting = Enum('Nesting', 'FRAME POST SUB NONE')
Block = nt('Block', ['name', 'nestb', 'nesti', 'subblock', 'subinline', 'parser'])
Inline = nt('Inline', ['name', 'nest', 'subscribe', 'escape', 'parser'])
InlineFrame = lambda name, escape, parser: Inline(name, Nesting.FRAME, ['inherit'], escape, parser)

def SingleGroupInlineFrame(name:str, start:str, end:str,
                           tag:str, attr:Mapping[str,str]=None):
  patt = re.compile(
    '(?<!\\\\)(?:\\\\\\\\)*\\K{0}(.*?(?<!\\\\)(?:\\\\\\\\)*){1}'.format(
      re.escape(start), re.escape(end)))
  return InlineFrame(name, set(stringcat(start, end)),
    [(patt, lambda groups: [tag, attr or {}, groups[0]])])

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
Underline = IdenticalInlineFrame('underline', '__', 'span', {'text-decoration': 'underline'})

CriticAdd = MirrorInlineFrame('critic-add', '{++', 'ins')
CriticDel = MirrorInlineFrame('critic-del', '{--', 'del')
CriticComment = MirrorInlineFrame('critic-comment', '{>>', 'span', {'class', 'critic comment'})

NoopBlock = Block(
  'noop',
  Nesting.FRAME,
  Nesting.POST,
  [],
  ['bold', 'italic', 'monospace'],
  lambda: ['div'])

def makeregistry(*args: Union[Block, Inline]):
  return dict((x.name, x) for x in args)

registry = makeregistry(Bold, Italic, Monospace, Underline, NoopBlock)
