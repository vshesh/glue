# This module generates SCSS from a pure-python css representation. It then
# uses libsass to generate a CSS string.

import sass
from itertools import takewhile

def scss_selector(selector: list, indent=1):
  selector_list = list(takewhile(lambda x: isinstance(x, str), selector))
  
  return (','.join(selector_list) + ' {'
          + ' '.join(
              item[0]+': '+item[1]+';' for item in selector[len(selector_list)].items())
          + ' '.join(scss_selector(x, indent+1) for x in selector[len(selector_list)+1:])
          + '}')

def scss(selectors:list):
  return sass.compile(string='\n\n'.join(map(scss_selector, selectors)))
