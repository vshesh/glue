#!/usr/bin/env python3

import regex as re
import inspect
import types
import toolz as t

# ----------------------- GENERAL UTILITIES ------------------------------

def unwind(g):
  """
  Unwinds a nested generator expression, returning built nested list.
  """
  l = []
  for e in g:
    if (isinstance(e, (list, types.GeneratorType, map, zip, filter))
        or inspect.isgenerator(e)
        or inspect.isgeneratorfunction(e)):
      l.append(unwind(e))
    else:
      l.append(e)
  return l

def cut(i, s):
  """cuts a string into two parts by a specified index"""
  return s[:i], s[i:]

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
  return next((i for i, j in enumerate(lst) if pred(j)), len(lst))

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
  # tokenize
  tokens = re.split(re.compile(r'^(?:(---[\w_=\- \.]*)|(\.\.\.))[ \t]*(?:\n|$)', re.M), text)

  l = []
  token = ''
  block = ''
  lineno = 1
  i = 0
  level = 0
  while i < len(tokens):
    if tokens[i] is None and tokens[i+1] == '...':
      # end of block
      level -= 1
      if level < 0:
        # end with no beginning
        raise ValueError('Block closing "..." found with no corresponding opening. at line {}'.format(lineno))
      elif level == 0:
        b = block.split(maxsplit=1)
        l.append([b[0], b[1].split() if len(b) > 1 else [], token])
        token = ''
      else:
        token += tokens[i+1] + "\n"
      i += 2
      lineno += 1
    elif tokens[i].startswith('---'):
      # begin of a new block
      level += 1
      if level == 1:
        block = tokens[i][3:]
        if len(token) > 0:
          l.append(token)
          token = ''
      else:
        token += tokens[i] + "\n"
      i += 2
      lineno += 1
    else:
      token += tokens[i]
      lineno += tokens[i].count('\n')
      i += 1

  if len(token) > 0:
    l.append(token)

  return l


def splicehtmlmap(f, html):
  """
  Generator that takes html in sexpr form and applies a function f to the
  leaf nodes (which are strings), then splices the result into the body.
  `f` should have signature `str` -> `list[sexpr form html elements]`
  eg f = lambda: [['div', 'hello world']]
  splicehtmlmap(f, ['body', '']) -> ['body', ['div', 'hello world']]
  """
  yield t.first(html)
  for e in t.drop(1, html):
    if isinstance(e, (list, tuple)):
      yield splicehtmlmap(f,e)
    elif isinstance(e, str):
      yield from f(e)
    else:
      yield e
