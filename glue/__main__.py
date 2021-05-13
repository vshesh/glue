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
  -a  --assets include all assets from registry in the output of the file.
  -m  --module python file containing a definition of a registry. Default is the Standard registry if this isn't included.
  -n  --name   the name of the component being generated if using a js library style output.
  -l  --language is the output language. can be one of html (default), elm, mithril, imba, or react. See the docs for instructions on how to add a different output language.
  """

if __name__ == '__main__':
  opts, args = getopt(sys.argv[1:], 'han:m:l:', ["help", 'assets', 'name=', 'module=','language='])
  language = 'html'
  registry_module = None
  name = 'UnidentifiedComponent'
  assets = False
  for (o,a) in opts:
    if o == '-h':
      print(usage())
      exit()
    if o == '-l' or o == '--language':
      language = a
    if o == '-m' or o == '--module':
      registry_module = a
    if o == '-n' or o == '--name':
      name = a
    if o == '-a' or o == '--assets':
      assets = True
  
  registry = importlib.import_module(registry_module).__getattribute__('registry') if registry_module else Standard
  
  def process(s: str, name: str) -> None:
    if assets: 
      print(registry.assets)
      return 
    if language == 'html':
      print(BeautifulSoup(codegen.tohtml(registry, s), 'html.parser').prettify())
    else:
      print(codegen.__getattribute__(f'render_{language}_component')(
        inflection.dasherize(inflection.underscore(name)) if language == 'imba' else name,
        codegen.__getattribute__(f'to{language}')(registry, s)))
  
  if len(args) == 0: process(sys.stdin.read(), name)
  else:
    for f in args:
      process(open(f).read(), inflection.camelize(inflection.underscore(path.splitext(path.basename(f))[0])))
