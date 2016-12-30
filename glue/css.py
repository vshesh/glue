# This module generates SCSS from a pure-python css representation. It then
# uses libsass to generate a CSS string.

import sass

def scss_selector(l: list, indent=1):
  return (l[0] + ' {'
          + ' '.join(
              item[0]+': '+item[1]+';' for item in l[1].items())
          + ' '.join(scss_selector(x, indent+1) for x in  (l[2:] if len(l) > 2 else []))
          + '}')

def scss(selectors:list):
  return sass.compile(string='\n\n'.join(map(scss_selector, selectors)))
