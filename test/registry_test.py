from glue.registry import *
from glue.elements import *
from glue.util import unwind

def test_registry_create():
  r = Registry(Monospace, Italic, Bold, Paragraphs)
  assert r[Monospace.name] == Monospace
  assert r[Italic.name] == Italic
  assert r[Bold.name] == Bold
  assert r[Paragraphs.name] == Paragraphs

def test_registry_elem_filters():
  r = Registry(Monospace, Italic, Bold, Paragraphs)
  assert set(r.all_block) == {Paragraphs}
  assert set(r.all_inline) == {Monospace, Italic, Bold}

def test_registry_subscriptions():
  r = Registry(Monospace, Italic, Bold, Paragraphs)
  assert set(r.inline_subscriptions(['all'])) == {Monospace, Italic, Bold}
  assert set(r.inline_subscriptions([Bold.name, Monospace.name])) == {Bold, Monospace}
  assert set(r.inline_subscriptions([])) == set()
  assert set(r.inline_subscriptions(['inherit'], Paragraphs)) == {Monospace, Italic, Bold}

def test_registry_merge():
  r = Registry(Monospace, Italic, Bold, Paragraphs)
  cr = Registry(CriticAdd, CriticComment, CriticDel, CriticHighlight)

  m = r | cr

  assert Monospace.name in m
  assert Bold.name in m
  assert Italic.name in m
  assert Paragraphs.name in m
  assert CriticAdd.name in m
  assert CriticHighlight.name in m
  assert CriticComment.name in m
  assert CriticDel.name in m

def test_registry_rename():
  r = Registry(Monospace, Italic, Bold, Paragraphs)
  m = r | {'monospace': {'name': 'mono'}}

  assert 'mono' in m
  assert Monospace.name not in m


