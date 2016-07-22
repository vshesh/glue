from bottle import Bottle, get, post, static_file, run
from app.params import params
from app.staticroute import staticroutestack
from glue import parse
from glue.util import unwind
from glue.library import Standard

app = Bottle()

@app.get('/')
def index():
  return static_file('index.html', root='static')

@app.post('/render')
@params(['text'])
def render(text: str):
  return {'template': unwind(parse(Standard, text))}

staticroutestack(app, ['js', 'css'], 'static')

if __name__ == '__main__':
  run(app, host='localhost', port='8000', reloader=True,
      debug=True)
