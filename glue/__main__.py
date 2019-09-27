import sys
from glue.codegen import *
from glue.library import Standard
from bs4 import BeautifulSoup
from getopt import getopt
import importlib

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
  s = sys.stdin.read()
  if language == 'html':
    print(BeautifulSoup(tohtml(registry, s), 'html.parser').prettify())
  elif language == 'mithril':
    print(render_mithril_component((args and args[0]) or 'UnidentifiedComponent', tomithril(registry, s)))
  elif language == 'react':
    print(render_react_component((args and args[0]) or 'UnidentifiedComponent', toreact(registry, s)))
  elif language == 'elm':
    print(render_elm_component((args and args[0]) or 'unidentifiedComponent'), toelm(registry, s))
