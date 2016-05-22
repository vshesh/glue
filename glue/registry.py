import toolz as t
from typing import Union, List
from glue.elements import *

class Registry(dict):
  def __init__(self, *args):
    super().__init__([(x.name, x) for x in args])
    
  @property
  def all_inline(self) -> List[Inline]:
    return t.filter(lambda x: isinstance(x, Inline), self.values())
    
  @property
  def all_block(self) -> List[Block]:
    return t.filter(lambda x: isinstance(x, Block), self.values())
  
  def inline_subscriptions(self, names:List[str], parent:Union[Block, Inline]):
    l = []
    if 'all' in names:
      l = self.all_inline
    if parent is not None and 'inherit' in names:
      l = t.concatv(l, (self[x] if isinstance(x, str) else x
                        for x in parent.subinline))
    
    return t.concatv(l, (self[x] if isinstance(x, str) else x
                         for x in names if x not in ('all', 'inherit')))
  
