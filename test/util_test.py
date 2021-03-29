from glue.util import *
from hypothesis import given
from hypothesis.strategies import text, integers
import string
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


# ------------- testing indented_tree ---------------------
def test_indented_tree_empty():
  assert indented_tree([]) == ''

@given(text())
def test_indented_tree_singleton(t):
  assert indented_tree([t]) == t

@given(text(), text())
def test_indented_tree_onesub(t, t2):
  assert indented_tree([t, t2]) == f'{t}\n  {t2}'

@given(text(min_size=1), text(min_size=1), text(min_size=1))
def test_indented_tree_doublesub(t, t2, t3):
  assert indented_tree([t, [t2, t3]]) == f'{t}\n  {t2}\n    {t3}'

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

def test_splitblocks_sidebyside():
  assert splitblocks(
    '---side-by-side\n---list |\nfirst item | hello  \n... | \n...') == [
           ['side-by-side', [], '---list |\nfirst item | hello  \n... | \n']]

# ----------------------- testing unpack ------------------------------

def test_unpack():
  assert unpack(
    ['h1', 'blah blah', ('Image', ['img', {'src': 'imageurl'}])]) == [
    'h1', 'blah blah', ['img', {'src': 'imageurl'}]]
  
# ----- test template2ast

@given(text())
def test_template_to_ast_string_identity(s: str):
  assert template_to_ast(s) == s


@given(text(alphabet=(string.ascii_letters+string.digits)))
def test_template_to_ast_tag_only(tag: str):
  assert template_to_ast(iter([tag])) == ({'tag' : tag, "attrs": {}, "body": []}
                                         if not tag or re.match(r'^[^A-Z]', tag) else
                                          {'name': tag, 'props': {}, 'children': []})

words = text(alphabet=(string.ascii_lowercase+string.digits+string.whitespace))

@given(tag=words, body=words)
def test_template_to_ast_no_attrs(tag: str, body: str):
  assert template_to_ast([tag, body]) == {'tag': tag, "attrs": {}, "body": [body]}

@given(words, words, words, words)
def test_template_to_ast_with_attrs(tag: str, attr: str, value: str, body: str):
  assert template_to_ast([tag, {attr: value}, body]) == {'tag': tag, "attrs": {attr: value} if value.strip() else {}, "body": [body]}

@given(words, words, words, words)
def test_template_to_ast_recursive(tag: str, attr: str, value: str, body: str):
  assert template_to_ast([tag, {attr: value}, [tag, {attr: value, tag:value}, body]]) == {
    'tag': tag,
    'attrs': {attr: value} if value.strip() else {},
    "body": [{'tag': tag, 'attrs': {attr: value, tag: value} if value.strip() else {}, 'body': [body]}]
  }


