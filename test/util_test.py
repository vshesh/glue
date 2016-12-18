from glue.util import *
import pytest


# ------------------------ general utilities testing -------------------


def test_cut():
  assert cut(1, 'xy') == ('x', 'y')
  assert cut(0, '') == ('', '')
  assert cut(0, 'x') == ('', 'x')
  assert cut(1, 'x') == ('x', '')

def test_stringcat():
  assert unwind(stringcat('a','b')) == ['a', 'b']
  assert unwind(stringcat('a', 'b', 'cd')) == ['a', 'b', 'c', 'd']
  assert unwind(stringcat('')) == []
  assert unwind(stringcat()) == []

def test_num_groups():
  assert num_groups(r'()') == 1
  assert num_groups(r'.*') == 0

def test_indexby():
  assert indexby(lambda x: x > 5, [1,4,5,6]) == 3
  assert indexby(lambda x: not isinstance(x, int), ['']) == 0

def test_fills():
  assert fills([1,1,1],1) == 1
  assert fills([2,1,1],3) == 2
  assert fills([4,5,4],1) == 0
  assert fills([1,1,1], 10) == 3



# ------------------------- testing splitblocks -------------------------



blockcontents = '''
Lorem ipsum dolor sit amet, consectetur adipisicing elit,
sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua. Ut enim ad minim veniam, quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
'''.lstrip()

noblock='''

Lorem ipsum dolor sit amet, consectetur adipisicing elit,
sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua. Ut enim ad minim veniam, quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

'''

def test_splitblocks_noblock():
  assert list(splitblocks(noblock)) == [noblock]

# spaces after beginning and end lines of block are PART of the test!
oneblock= '''some text

---block
Lorem ipsum dolor sit amet, consectetur adipisicing elit,
sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua. Ut enim ad minim veniam, quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
...
'''

def test_splitblocks_oneblock():
  assert list(splitblocks(oneblock)) == ['some text\n\n', ['block', [], blockcontents]]

twoblock='''some text
---block
Lorem ipsum dolor sit amet, consectetur adipisicing elit,
sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua. Ut enim ad minim veniam, quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
...

some text
---block
Lorem ipsum dolor sit amet, consectetur adipisicing elit,
sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua. Ut enim ad minim veniam, quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
...
'''

def test_splitblocks_twoblock():
  assert list(splitblocks(twoblock)) == [
  'some text\n', ['block', [], blockcontents],
  '\nsome text\n', ['block', [], blockcontents]]


nestblock = '''some text
---block
Lorem ipsum dolor sit amet, consectetur adipisicing elit,
sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua. Ut enim ad minim veniam, quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
---block
Lorem ipsum dolor sit amet, consectetur adipisicing elit,
sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua. Ut enim ad minim veniam, quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
...
...
'''

def test_splitblocks_nestblock():
  assert list(splitblocks(nestblock)) == [
  'some text\n', ['block', [], blockcontents + '---block\n'+blockcontents+'...\n']]

def test_splitblocks_args():
  assert list(splitblocks('---block -x y z\n...')) == [['block', ['-x', 'y', 'z'], '']]


def test_splitblocks_error():
  with pytest.raises(ValueError):
    splitblocks('...')

  with pytest.raises(ValueError) as e:
    splitblocks('---b\n...\n...\n')
  assert 'line 3' in str(e.value)

# ----------------------- testing unpack ------------------------------

def test_unpack():
  assert unpack(['h1', 'blah blah', ('Image', ['img', {'src': 'imageurl'}])]) == ['h1', 'blah blah', ['img', {'src': 'imageurl'}]]