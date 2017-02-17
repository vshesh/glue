import bottle
bottle.TEMPLATE_PATH.append('./static/templates')

from bottle import Bottle, static_file, template, run
from app.params import params, jsonabort
from app.staticroute import staticroutestack
import glue
from glue import parse, tohtml
from glue.util import unwind, unpack
from glue.library import Standard

app = Bottle()

@app.get('/')
def index():
  return static_file('index.html', root='static')

@app.post('/render')
@params(['text'])
def render(text: str):
  try:
    return {'template': unwind(parse(Standard, text))}
  except (ValueError, TypeError) as e:
    jsonabort(400, str(e))

staticroutestack(app, ['js', 'css'], 'static')

@app.get('/example')
@params(['path'])
def example(path: str):
  try:
    with open('./static/examples/' + path + '.txt') as file:
      r = parse(Standard, file.read())
      return glue.codegen.render(unwind(r))
  except (ValueError, TypeError) as e:
    jsonabort(400, str(e))


@app.get('/blocknames')
def blockinfo():
  return {'blocks': { x.name:x.parser.__doc__ for x in Standard.all_block}}

if __name__ == '__main__':
  # generate index.html
  with open('./static/index.html', 'w') as index:
    index.write(template('index', assets=Standard.assets))
  with open('./gh-pages/index.html', 'w') as index:
    index.write(template('index', assets=Standard.assets))

  run(app, host='localhost', port='8000', reloader=True,
      debug=True)
