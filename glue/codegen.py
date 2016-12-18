import toolz as t

from glue.html import render
from glue.parser import parse

tohtml = t.compose(render, parse)

def render_mithril(html):
  if html is None: return ''
  elif isinstance(html, list):
    if html[0][0].isupper():
      return 'm.component({}, {})'.format(html[0], html[1])
    elif isinstance(html[1], dict):
      return 'm({}, {}, {})'.format(html[0], html[1], ', '.join(map(render_mithril, html[2:])))
    return 'm({}, {})'.format(html[0], ', '.join(map(render_mithril, html[1:])))
  elif isinstance(html, str):
    return repr(html)
  else:
    raise ValueError('{} is not convertible into html'.format(html))

tomithril = t.compose(render_mithril, parse)

