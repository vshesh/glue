import traceback

import bottle
bottle.TEMPLATE_PATH.append('./static/templates')

from bottle import Bottle, static_file, template, run
from app.params import params, jsonabort
from app.staticroute import staticroutestack
import glue
from glue import parse, tohtml
from glue.util import unwind, template_to_ast, unpack
from glue.library import Standard

app = Bottle()

@app.get('/')
def index():
  return static_file('index.html', root='static')

@app.post('/render')
@params(['text'], {'name': ''})
def render(text: str, name: str):
  try:
    return template_to_ast(parse(
      Standard,
      text if name == '' else '---'+name+'\n'+text+'\n...'))
  except (ValueError, TypeError) as e:
    traceback.print_exc()
    jsonabort(400, str(e))

staticroutestack(app, ['js', 'css'], 'static')

@app.post('/blocknames')
def blockinfo():
  return {'blocks': { x.name:x.parser.__doc__ or '' for x in Standard.all_block}}

if __name__ == '__main__':
  # generate index.html
  with open('./static/index.html', 'w') as index:
    index.write(template('index', assets=Standard.assets))
  with open('./glue-notebook/src/index.html', 'w') as index:
    index.write(template('index', assets=Standard.assets))

  run(app, host='localhost', port='8000', reloader=True,
      debug=True)
