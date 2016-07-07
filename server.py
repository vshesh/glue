from bottle import Bottle, get, post, static_file, run
from app.params import params
from app.staticroute import staticroutestack

app = Bottle()

@app.get('/')
def index():
  return static_file('index.html', root='app')

@app.post('/render')
@params(['text'])
def render(text: str):
  return {'template': parse(text, Standard)}

staticroutestack(app, ['js', 'css'], 'app')

if __name__ == '__main__':
  run(app, host='localhost', port='8000', reloader=True)
