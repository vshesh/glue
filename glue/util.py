#!/usr/bin/env python3

import regex as re
import toolz as t

# ----------------------- GENERAL UTILITIES ------------------------------

def cut(i, s):
  """cuts a string into two parts by a specified index"""
  return (s[:i], s[i:])

def stringcat(*s:str):
  """
  generator that returns each character in a sequence of strings.
  It's just lazy string concatenation.
  """
  for string in s:
    for c in string:
      yield c

def num_groups(regex):
  """the number of groups that a regex will capture."""
  return re.compile(regex).groups

def indexby(pred, lst):
  """gives index of first item in list for which pred(item) is True"""
  return next(i for i, j in enumerate(lst) if pred(j))

def fills(quantities, n):
  """
  fills([1,1,1],1) => 1
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

# ------------------------- PROJECT SPECIFIC UTILITIES --------------------


def splitblocks(text:str):
  """
  Given some block of text, returns a seq that has a string element for
  the text in between blocks, and a pair list element with
  [dispatch, body] for the blocks. The dispatch is everything on the `---` line,
  and the body is everything after that line and before the `...` at the end.
  """
  return t.map(lambda b: b[3:].split('\n', 1) if b.startswith('---') else b,
               re.split(re.compile(r'\n(---(?:.|\n)*?)\n\.\.\.\n', re.MULTILINE),
                        text))

def splicehtmlmap(f, html):
  """
  Generator that takes html in sexpr form and applies a function f to the
  leaf nodes (which are strings), then splices the result into the body.
  `f` should have signature `str` -> `list[sexpr form html elements]`
  eg f = lambda: [['div', 'hello world']]
  splicehtmlmap(f, ['body', '']) -> ['body', ['div', 'hello world']]
  """
  yield html[0]
  for e in html[1:]:
    if isinstance(e, (list, tuple)):
      yield splicehtmlmap(f,e)
    elif isinstance(e, str):
      yield from f(e)
    else:
      yield e
