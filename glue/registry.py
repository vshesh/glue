# # Registry
# Created: May 21, 2016
# Author: Vishesh Gupta

from collections import OrderedDict
import copy
import toolz as t
from typing import Union, List, Mapping, Iterable
from glue.elements import *

class Registry(OrderedDict, Mapping[str, Element]):
  """
  Registry class is some convenience functions tacked onto
  a dictionary that maps names (strings) to elements (Inline or Block).

  The idea is that you can treat registries like sets and do merge to combine
  or update them, or subtract to remove keys, etc.

  r = Registry(...)
  r |= {'name': {'property': 'new-value'}}
  r -= ['name1', 'name2']
  """

  TOP = 'TOP'

  def __init__(self, *args:Union[Inline, Block], top=None, **kwargs):
    super().__init__([(x.name, x) for x in args])
    if top is not None:
      self[Registry.TOP] = top

  def __iadd__(self, other):
    if not all(isinstance(x, (Inline, Block)) for x in other):
      return NotImplemented

    for k in other:
      self[k.name] = k

    return self

  def __ior__(self, other:dict):
    if not isinstance(other, dict):
      return NotImplemented
    # clobber self with what is in dict.
    for k in other:
      otheritem = other[k]
      if k not in self:
        self[k] = otheritem
      else:
        if isinstance(otheritem, (Inline, Block)):
          self[k] = otheritem
        elif isinstance(otheritem, dict):
          newitem = self[k]._replace(**otheritem)
          if 'name' in otheritem:
            del self[k]
            self[otheritem['name']] = newitem
          else:
            self[k] = newitem

    return self

  def __isub__(self, other: Iterable):
    if not isinstance(other, dict) and (
          not isinstance(other, Iterable) or
          not all(isinstance(x, (Inline, Block)) for x in other)):
      return NotImplemented
    # remove keys from sub that aren't in dict
    for k in other:
      key = k.name if isinstance(k, (Inline, Block)) else k
      if key in self:
          del self[key]

    return self

  def __or__(self, other:dict):
    if not isinstance(other, dict):
      return NotImplemented

    r = copy.copy(self)
    r |= other
    return r

  def __sub__(self, other:Union[dict, Iterable]):
    if not isinstance(other, dict) and (
        not isinstance(other, Iterable) or
        not all(isinstance(x, (Inline, Block)) for x in other)):
      return NotImplemented

    r = copy.copy(self)
    r -= other
    return r

  def __add__(self, other:Iterable):
    if not all(isinstance(x, (Inline, Block)) for x in other):
      return NotImplemented

    r = copy.copy(self)
    r += other
    return r

  @property
  def top(self) -> Element:
    return self[Registry.TOP]
  
  def set_top(self, e: Element):
    self[Registry.TOP] = e

  @property
  def all_inline(self) -> List[Inline]:
    return t.filter(lambda x: isinstance(x, Inline), self.values())

  @property
  def all_block(self) -> List[Block]:
    return t.filter(lambda x: isinstance(x, Block), self.values())

  def inline_subscriptions(self, names:List[str], parent:Element=None) -> List[Inline]:
    l = []
    if 'all' in names:
      l.extend(self.all_inline)
    if parent is not None and 'inherit' in names:
      if 'all' not in names and 'all' in parent.subinline:
        l += self.all_inline
      l.extend(self[x] if isinstance(x, str) else x
               for x in parent.subinline if x != 'all')

    l.extend(self[x] if isinstance(x, str) else x
             for x in names if x not in ('all', 'inherit'))
    return l

  @property
  def assets(self) -> str:
    """
    Returns all the assets of every element in the registry combined as a string.
    Each asset is kept in its own tag, with no concatenation of scripts or
    stylesheets.
    :return: a string which contains all the assets, to be put into an HTML template.
    """
    return '\n\n\n'.join('\n'.join(item[1].assets) for item in self.items() if len(item[1].assets) > 0)
  
  def validate(self) -> bool:
    if self.TOP not in self or not isinstance(self[self.TOP], Block):
      return False

    sub = set()
    for e in self.values():
      sub.union(e.sub)
      if not e.validate(): return False

    for e in sub:
      if e.name not in ('all', 'inherit') and e.name not in self:
        return False

    return True
