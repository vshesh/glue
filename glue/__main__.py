import sys
from glue.codegen import *
from glue.library import Standard
from bs4 import BeautifulSoup
from getopt import getopt


if __name__ == '__main__':
  opts, args = getopt(sys.argv[1:], 'l:', ['language='])
  language = 'html'
  for (o,a) in opts:
    if o == '-l' or o == '--language':
      language = a
  s = sys.stdin.read()
  if language == 'html':
    print(BeautifulSoup(tohtml(Standard, s), 'html.parser').prettify())
  elif language == 'mithril':
    print(render_mithril_component((args and args[0]) or 'UnidentifiedComponent', tomithril(Standard, s)))
  elif language == 'react':
    print(render_react_component((args and args[0]) or 'UnidentifiedComponent', toreact(Standard, s)))
  elif language == 'elm':
    print(render_elm_component((args and args[0]) or 'unidentifiedComponent'), toelm(Standard, s))
