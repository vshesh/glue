# File: html_test.py
# tests that the html parser works as expected.
# note, html.py is copied from cottonmouth, so the tests are not *that*
# rigorous. I copied the unittest test case from cottonmouth.py as well.

import unittest

from glue.html import *
from bs4 import BeautifulSoup
from collections import OrderedDict as odict


def html_equiv(h1, h2):
  return BeautifulSoup(h1, features="html.parser") == BeautifulSoup(h2, features="html.parser")


class TestHTML(unittest.TestCase):
  def test_p_with_content(self):
    self.assertEqual(render(['p', 'paragraph']), '<p>paragraph</p>')
  
  def test_p_with_style_dict(self):
    assert html_equiv(render(['p', {'style': odict([('display', 'inline-block'), ('color', 'red')])}, 'hello world']),
                      '<p style="display:inline-block;color:red;">hello world</p>')
  
  def test_div_shortcut_with_content(self):
    assert html_equiv(
      render(['#my.test', 'testing']),
      '<div id="my" class="test">testing</div>'
    )
  
  def test_image(self):
    self.assertEqual(
      render(['img', {'src': 'image.png'}]),
      '<img src="image.png">'
    )
  
  def test_embedded_content_with_conditional_list_item(self):
    image = ['img', {'src': 'embedded.jpg'}]
    assert html_equiv(
      render(['#container', {'data-attr': '123'},
              image, ['hr'],
              ['ul',
               ['li', 'A'],
               ['li', 'B'],
               ['li', 'C'],
               ['li', 'D'],
               ['li', 'Z'] if False else None]]),
      ('<div id="container" data-attr="123">'
       '<img src="embedded.jpg"><hr>'
       '<ul><li>A</li><li>B</li><li>C</li><li>D</li></ul>'
       '</div>')
    )
  
  def test_generator(self):
    self.assertEqual(
      render(['#container',
              ['ul', (['li', l] for l in 'ABCDXYZ' if l < 'X')]]),
      ('<div id="container">'
       '<ul><li>A</li><li>B</li><li>C</li><li>D</li></ul>'
       '</div>')
    )
  
  def test_callable(self):
    say_hello = lambda name: ['p', 'Hello, {}!'.format(name)]
    self.assertEqual(
      render(['#container', say_hello], name='USER'),
      '<div id="container"><p>Hello, USER!</p></div>'
    )
  
  def test_p_tag(self):
    assert render(['#container', ['p', 'paragraph 2']]) == '<div id="container"><p>paragraph 2</p></div>'
  
  def test_readme_example(self):
    def welcome(user=None, **context):
      return ['p', 'Welcome' + (' back!' if user else '!')]
    
    content = (
      '<!doctype html>',
      ['html',
       ['head',
        ['title', 'The Site'],
        ['meta', {'http-equiv': 'content-type',
                  'content': 'text/html;charset=utf-8'}],
        ['link', dict(rel='stylesheet', type='text/css',
                      href='static/layout.css')]],
       ['body',
        ['h1#header', 'Welcome to the site!'],
        ['#map.pretty-map'],
        ['#main', welcome]]]
    )
    self.assertTrue(isinstance(render(*content), str))
  
  def test_unicode_coercion(self):
    object_ = object()
    content = ['p', object_]
    self.assertEqual(
      render(content),
      u'<p>{}</p>'.format(object_)
    )
  
  def test_render_class(self):
    assert render(['tag', {'class': 'name'}]) == u'<tag class="name"></tag>'
    assert render(['tag', {'class': ['name']}]) == u'<tag class="name"></tag>'


if __name__ == '__main__':
  unittest.main()
