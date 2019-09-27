#!/usr/bin/env python3
from typing import Mapping
from collections import defaultdict
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

def splitblocks(text: str):
  """
  A state machine type parser that can split the original document into nested blocks.

  It scans for groups of --- and ... on their own lines, and then uses those tokens
  to make a tree of blocks for the parser.
  :param text: raw text from the input file to the glue parser
  :return: a `X = str | [X]` type structure that represents the structure of the AST of the document.
  """
  # tokenize
  tokens = re.split(re.compile(r'^(?:(---[\w_=\- \.]+)|(\.\.\.))[ \t]*(?:\n|$)', re.M), text)

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
    elif re.match(r'^---[\w_=\- \.]+$', tokens[i]):
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

istag = lambda html: (
  isinstance(html, (type(iter([])), types.GeneratorType, map, zip, filter))
  or inspect.isgeneratorfunction(html)
  or inspect.isgenerator(html))

def parsetag(tag: str):
  """
  Takes a complex tag, like: tag#id.class1.class2, or tag.class1#id.class2
  where the id could occur anywhere or the classes could occur anywhere
  
  **returns**: a tuple of (str, {'id':str, 'class':str}). the first is the tag name,
               and the second is an attrs dictionary prepopulated with the id and class from this tag.
  """
  if '.' not in tag and '#' not in tag: return tag, {'id': '', 'class': ''}
  if '#' not in tag:
    tag, *classes = tag.split('.')
    return tag, {'class': ' '.join(classes), 'id': ''}
  
  one, two = tag.split('#', maxsplit=1) # there should only be one of these.
  tag, *c1 = one.split('.')
  id, *c2 = two.split('.')
  
  return tag, {'id': id, 'class': ' '.join(t.concatv(c1, c2))}

def unpack(html):
  """
  Unpacks the annotated HTML style form returned by `parseinline`.
  Gives the raw HTML in cottonmouth template form.
  This function is a noop on cottonmouth html.
  
  :param html: Annotated HTML as returned by parseinline. For each snippet of
  HTML generated by some inline or block element, the html param should contain
  a tuple like `(elem, [html...])` which will be unpacked, yielding only the
  HTML.
  :return: `(elem, [html...])` -> `[html...]` for each element in HTML. the tag
  name and attribute list are ignored.
  """
  if istag(html):
    return [unpack(x) for x in html]
  elif isinstance(html, tuple):
    if isinstance(html[1][1], dict):
      return [html[1][0], html[1][1], *map(unpack, html[1][2:])]
    return [html[1][0], *map(unpack, html[1][1:])]
  elif isinstance(html, list):
    return [html[0], *map(unpack, html[1:])]
  else:
    return html

def assemble_ast(tag:str, idsclasses: Mapping[str, str], attrs: Mapping[str, str], body: list):
  """
  Small helper function for the template_2_ast function that assembles the appropriate ast element
  given the tag name, a dictionary of ids/classes from the tag name, further attrs, and a list of children or the body.
  For most components, there won't be any children.
  
  :param tag:
  :param idsclasses:
  :param attrs:
  :param body:
  :return:
  """
  iscomponent = re.match(r'^[A-Z]', tag)
  attrs['id'] = (attrs.get('id', '') + ' ' + idsclasses.get('id', '')).strip()
  attrs['class'] = (attrs.get('class', '') + ' ' + idsclasses.get('class', '')).strip()
  # remove the empty attributes to avoid clutter and save bytes.
  attrs = dict(t.valfilter(lambda x: not (isinstance(x, str) and x.strip() == ''), attrs))
  # special handling for the "style" attribute, since that can be a dictionary
  attrs = t.valmap(lambda val:' '.join('{}: {};'.format(k,v) for k,v in val.items())
                   if isinstance(val, dict) else val,
                   attrs)
  
  if iscomponent:
    return {'name': tag, 'props': attrs, 'children': body}
  else:
    return {'tag': tag, 'attrs': attrs, 'body': body}
  
  
def template_to_ast(html):
  """
  Converts cottonmouth type HTML to an "AST" representation, where there can be two kinds of
  structural types - one is {tag, attrs, body} for the normal HTML, and the other is {name, props, children}
  for the components.
  
  There are two separate ones on purpose so its easy to tell which should be handled as a subcomponent and which
  should be handled as an HTML tag as part of a vdom templating library.
  Eg, in Elm this makes things a lot easier.
  
  """
  if isinstance(html, str): return html
  if isinstance(html, list):
    hasattrs = len(html) > 1 and isinstance(html[1], dict)
    tag, idsclasses = parsetag(html[0])
    # combine attrs with idsclasses in the tag name. only modifies these two properties explicitly, so that
    # other attrs and data for components is untouched.
    attrs = html[1] if hasattrs else {}
    return assemble_ast(tag, idsclasses, attrs, [template_to_ast(x) for x in html[(2 if hasattrs else 1):] if x is not None])
  
  if istag(html):
    tag,html = t.peek(html)
    if istag(tag):
      return map(template_to_ast, html)
    # this looks confusing, but it's to leave the generator at the right place,
    # and also extract the tag and attrs.
    # because I have to check the type of the next element, and optionally consume it if it's the right one
    # I end up assigning next(html) to a particular variable twice.
    tag, idsclasses = parsetag(next(html))
    try:
      attrs, html = t.peek(html)
      attrs = next(html) if isinstance(attrs, dict) else {}
    except StopIteration:
      attrs = {}
      html = iter([])
    return assemble_ast(tag, idsclasses, attrs, [template_to_ast(x) for x in html if x is not None])
  
  else: raise ValueError('template_to_ast: Cannot convert the following type of value: ' + str(html))
  
