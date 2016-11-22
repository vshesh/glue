from glue.elements import *
import regex as re

def test_block_decorator():


  def IdentityBlock(text):
    "mock docstring"
    return ['p', text]

  b = block()(IdentityBlock)

  assert b.name == 'identity-block'
  assert b.nest == Nesting.POST
  assert b.sub == ['all']
  assert b.subinline == ['all']
  assert b.parser.__doc__ == "mock docstring"

  b2 = block(nest=Nesting.NONE,
             sub=['b1', 'i1', 'i2'])(IdentityBlock)

  assert b2.name == 'identity-block'
  assert b2.nest == Nesting.NONE
  assert b2.sub == ['b1', 'i1', 'i2']
  assert b2.subinline == []
  assert b2.parser.__doc__ == "mock docstring"


def test_inline_decorator():

  def IdentityInline(text):
    "mock docstring"
    return ['span', text]

  i = inline(r'.*')(IdentityInline)

  assert i.name == 'identity-inline'
  assert i.nest == Nesting.FRAME
  assert i.subinline == ['all']
  assert i.escape == ''
  assert i.regex == re.compile(r'.*')
  assert i.parser.__doc__ == 'mock docstring'


  i = inline(r'\\.*', nest=Nesting.POST, escape="*", sub=['all'])(IdentityInline)

  assert i.name == 'identity-inline'
  assert i.nest == Nesting.POST
  assert i.subinline == ['all']
  assert i.escape == '*'
  assert i.regex == re.compile(r'\\.*')
  assert i.parser.__doc__ == 'mock docstring'


def test_replace():

  def IdentityInline(text):
    "mock docstring"
    return ['span', text]

  i = inline(r'.*')(IdentityInline)

  assert i.name == 'identity-inline'
  assert i.nest == Nesting.FRAME
  assert i.subinline == ['all']
  assert i.escape == ''
  assert i.regex == re.compile(r'.*')
  assert i.parser.__doc__ == 'mock docstring'

  newi = i._replace(name='new-name')

  assert newi.name == 'new-name'
  assert i.name == 'identity-inline'
  assert i != newi
  assert i is not newi
