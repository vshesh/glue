from distutils.core import setup

setup(
  name="glue",
  version="0.0.1",
  description="Plain text syntax for other plain text syntaxes",
  author="Vishesh Gupta",
  author_email="vishesh@cs.stanford.edu",
  url="https://github.com/vshesh/glue",
  packages=['glue', 'test'],
  py_modules=['server.py'],
  license='GPLv3'
)

