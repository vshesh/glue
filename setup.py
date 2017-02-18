from distutils.core import setup

setup(
  name="glue",
  version="0.1.0",
  description="Plain text syntax for other plain text syntaxes",
  long_description=open('README.md').read(),
  author="Vishesh Gupta",
  author_email="vishesh@cs.stanford.edu",
  url="https://github.com/vshesh/glue",
  packages=['glue', 'test'],
  license='GPLv3',
  install_requires=['regex', 'libsass', 'simplejson', 'toolz', 'ruamel.yaml', 'inflection', 'bs4']
)

