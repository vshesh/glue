# File: staticroute.py
# Author: Vishesh Gupta
# Created: June 2015

from bottle import static_file
import os.path

def staticroute(app, name, root='static'):
  app.route('/'.join(['', name, '<resource:path>']), ['GET'],
    lambda resource: static_file(resource, os.path.join(root, name)))


def staticroutestack(app, folders, root='static'):
  for f in folders:
    staticroute(app, f, root)
