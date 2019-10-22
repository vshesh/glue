import sys
import glue.codegen as codegen
from glue.library import Standard
from bs4 import BeautifulSoup
from getopt import getopt
import importlib
import os.path as path
import inflection

def usage():
  return """
  glue [hm:l:]
  
  Converts a text file into some form of rich output, either HTML, a
  frontend component library (mithril, react, etc) or a raw compiler template
  type of output ({tag: ..., attrs: ..., body: [...]}).
  
  -h  this help message
  -m  --module python file containing a definition of a registry. Default is the Standard registry if this isn't included.
  -l  --language is the output language. can be one of html (default), elm, mithril, or react. See the docs for instructions on how to add a different output language.
  """

if __name__ == '__main__':
  opts, args = getopt(sys.argv[1:], 'hm:l:', ["help", 'module=','language='])
  language = 'html'
  registry_module = None
  for (o,a) in opts:
    if o == '-h':
      print(usage())
      exit()
    if o == '-l' or o == '--language':
      language = a
    if o == '-m' or o == '--module':
      registry_module = a
  
  registry = importlib.import_module(registry_module).__getattribute__('registry') if registry_module else Standard
  
  def process(s: str, name: str) -> None:
    if language == 'html':
      print(BeautifulSoup(tohtml(registry, s), 'html.parser').prettify())
    else:
      print(codegen.__getattribute__(f'render_{language}_component')(
        name,
        codegen.__getattribute__(f'to{language}')(registry, s)))
  
  if len(args) == 0: process(sys.stdin.read(), 'UnidentifiedComponent')
  else:
    for f in args:
      process(open(f).read(), inflection.camelize(inflection.underscore(path.splitext(path.basename(f))[0])))
