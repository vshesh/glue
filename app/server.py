from bottle import Bottle, run, route, static_file
from server.params import params
from server.staticroute import staticroutestack


app = Bottle()

@app.route('/')
def index():
  return static_file('index.html', root='server')

staticroutestack(app, ['js', 'css'], 'server')

run(app, host='localhost', port='8000', reloader=True)
