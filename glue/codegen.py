import toolz as t

from glue.util import unwind
from glue.html import render
from glue.parser import parse
from inflection import camelize

def attr_values_to_str(attrs: dict):
  return str({k: ' '.join('{}:{};'.format(k2,v2) for k2,v2 in v)
              if isinstance(v, dict)
              else v})

def render_mithril(html) -> str:
  """
  Takes html in cottonmouth syntax and generates a mithril template from it.
  
  ### Params
  * html see cottonmouth - ['div', {'attr': 'value'}, 'text' ...] is the general syntax.
  
  ### Return
  a string that is a valid mithril template of the same HTML.
  """
  if html is None: return ''
  elif isinstance(html, list):
    if isinstance(html[0], list):
      # nested list, need to unpack:
      return '[{}]'.format(','.join(render_mithril(x) for x in html))
    else:
      tag = repr(html[0])
      attr = (str(attr_values_to_str(html[1])).replace('True', 'true').replace('False', 'false')
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


def double_quoted_repr(s: str):
  return '"' + repr(s)[1:-1].replace('"', '\\"') + '"'

def render_elm_attrs(attrs: dict):
  return ', '.join(['attribute {} {}'.format(double_quoted_repr(k),double_quoted_repr(v))
                    for (k,v) in attr_values_to_str(attrs.items())])

def render_elm(html):
  """
  Generate an Elm template that can be used as part of a view function.
  Elm is a bit more particular about the generated template than mithril. First, the template must have a root node.
  At no time can you have a list of list of nodes, either.
  :param html:
  :return:
  """
  if html is None: return ''
  elif isinstance(html, list):
    if isinstance(html[0], list):
      # nested list, need to unpack:
      return '{}'.format(','.join(render_elm(x) for x in html))
    else:
      tag = double_quoted_repr(html[0])
      attr = render_elm_attrs(html[1]
              if len(html) > 1 and isinstance(html[1], dict)
              else {})
      if tag[1].isupper():
        # components are not well supported this way in Elm. They are more complicated than just adding a call to a
        # known wrapper function.
        # return 'm.component({}, {})'.format(html[0], attr)
        return ''
      elif len(html) == 1:
        return 'Html.node {tag} [] []'.format(tag=tag)
      elif len(html) == 2 and isinstance(html[1], dict):
        return 'Html.node {} [{}] []'.format(tag, attr)
      elif len(html) >= 3 and isinstance(html[1], dict):
        return 'Html.node {} [{}] [{}]'.format(tag, attr,
                                      ', '.join(map(render_elm, html[2:])))
    # no attr dictionary
    return 'Html.node {} [] [{}]'.format(tag, ', '.join(map(render_elm, html[1:])))
  elif isinstance(html, str):
    return 'text ' + double_quoted_repr(html)
  else:
    raise ValueError('{} is not convertible into html'.format(html))


def render_elm_component(name: str, expr: str):
  return '''{name} : Html Msg
  {name} = {expr}
  '''.format(name=name, expr=expr)

tohtml = t.compose(render, parse)
tomithril = t.compose(render_mithril, unwind, parse)
toreact = t.compose(render, parse)
toelm = t.compose(render_elm, unwind, parse)
