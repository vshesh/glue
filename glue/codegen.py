import toolz as t

from glue.util import unwind
from glue.html import render
from glue.parser import parse
from inflection import camelize

tohtml = t.compose(render, parse)

def render_mithril(html):
  if html is None: return ''
  elif isinstance(html, list):
    if isinstance(html[0], list):
      # nested list, need to unpack:
      return '[{}]'.format(','.join(render_mithril(x) for x in html))
    else:
      tag = repr(html[0])
      attr = (str(html[1]).replace('True', 'true').replace('False', 'false')
              if len(html) > 1 and isinstance(html[1], dict)
              else {})
      if tag[1].isupper():
        return 'm.component({}, {})'.format(html[0], attr)
      elif len(html) == 1:
        return 'm(' + tag + ')'
      elif len(html) == 2 and isinstance(html[1], dict):
        return 'm({}, {})'.format(tag, attr)
      elif len(html) >= 3 and isinstance(html[1], dict):
        return 'm({}, {}, {})'.format(tag, attr,
                                      ', '.join(map(render_mithril, html[2:])))
    # no attr dictionary
    return 'm({}, {})'.format(tag, ', '.join(map(render_mithril, html[1:])))
  elif isinstance(html, str):
    return repr(html)
  else:
    raise ValueError('{} is not convertible into html'.format(html))

def render_mithril_component(name: str, expr: str):
  """
  Wraps expr such that it is a mithril component rather than just an expression.
  This way it can be used for mounting, routes, etc.

  :param name: name of the component. the casing is auto-generated for sanity.
  :param expr: expr that forms the view, something like `m('div', 'Hello World')`
     full details are available as part of the mithril docs.

  :return: this string:
    `var NAME = {controller: () => null, view: function() { return EXPR;} };`
  """

  return '''var {name} = {{
    view: function() {{
      return {expr};
    }}
  }};
  '''.format(name=camelize(name), expr=expr)

def render_react_component(name: str, expr: str):
  return '''var {name} = React.createClass({{
    render: function() {{
      return {expr};
    }}
  }}'''.format(name=name, expr=expr)

tomithril = t.compose(render_mithril, unwind, parse)
toreact = t.compose(render, parse)

