from glue.elements import *
import regex as re

def test_block_decorator():


  def IdentityBlock(text):
    "mock docstring"
    return ['p', text]

  b = block()(IdentityBlock)

  assert b.name == 'identity-block'
  assert b.nest == Nesting.POST
  assert b.subblock == ['all']
  assert b.subinline == ['all']
  assert b.parser.__doc__ == "mock docstring"

  b2 = block(nest=Nesting.NONE,
             subblock=['b1'],
             subinline=['i1', 'i2'])(IdentityBlock)

  assert b2.name == 'identity-block'
  assert b2.nest == Nesting.NONE
  assert b2.subblock == ['b1']
  assert b2.subinline == ['i1', 'i2']
  assert b2.parser.__doc__ == "mock docstring"


def test_inlineone_decorator():

  def IdentityInline(text):
    "mock docstring"
    return ['span', text]

  i = inlineone(r'.*')(IdentityInline)

  assert i.name == 'identity-inline'
  assert i.nest == Nesting.FRAME
  assert i.subinline == ['inherit']
  assert i.escape == ''
  assert i.parser[0][0] == re.compile(r'.*')
  assert i.parser[0][1].__doc__ == 'mock docstring'


  i = inlineone(r'\\.*', nest=Nesting.POST, escape="*", subinline=['all'])(IdentityInline)

  assert i.name == 'identity-inline'
  assert i.nest == Nesting.POST
  assert i.subinline == ['all']
  assert i.escape == '*'
  assert i.parser[0][0] == re.compile(r'\\.*')
  assert i.parser[0][1].__doc__ == 'mock docstring'
