import copy
import toolz as t
from typing import Union, List, Mapping, Iterable
from glue.elements import *


class Registry(dict, Mapping[str, Union[Inline, Block]]):
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

  def __isub__(self, other:dict):
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
  def top(self) -> Union[Inline,Block]:
    return self[Registry.TOP]

  @property
  def all_inline(self) -> List[Inline]:
    return t.filter(lambda x: isinstance(x, Inline), self.values())

  @property
  def all_block(self) -> List[Block]:
    return t.filter(lambda x: isinstance(x, Block), self.values())

  def inline_subscriptions(self, names:List[str], parent:Union[Block, Inline]=None) -> List[Inline]:
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

