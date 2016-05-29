import toolz as t
from typing import Union, List, Mapping
from glue.elements import *

class Registry(dict, Mapping[str, Union[Inline, Block]]):
  def __init__(self, *args:Union[Inline, Block]):
    super().__init__([(x.name, x) for x in args])

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

  def __or__(self, other:dict):
    r = Registry(*self.values())
    r |= other
    return r

  @property
  def all_inline(self) -> List[Inline]:
    return t.filter(lambda x: isinstance(x, Inline), self.values())

  @property
  def all_block(self) -> List[Block]:
    return t.filter(lambda x: isinstance(x, Block), self.values())

  def inline_subscriptions(self, names:List[str], parent:Union[Block, Inline]=None):
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

