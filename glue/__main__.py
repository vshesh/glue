import sys
from glue.parser import tohtml
from glue.library import Standard
from bs4 import BeautifulSoup

if __name__ == '__main__':
  print(BeautifulSoup(tohtml(Standard, sys.stdin.read()), 'html.parser').prettify())
