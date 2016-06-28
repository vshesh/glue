
from glue import parse
from glue.library import *
from glue.util import unwind


def test_header():
  assert unwind(parse(Registry(Paragraphs, Header), '# h1', Paragraphs)) == ['div', ['h1', ' h1']]
  assert unwind(parse(Registry(Paragraphs, Header), '# h1\n## h2\n### h3', Paragraphs)) == ['div', ['h1', ' h1'], ['h2', ' h2'], ['h3', ' h3']]
