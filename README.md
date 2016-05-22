# Glue: plain-text format for other plain-text formats

[![Build Status](https://travis-ci.org/vshesh/glue.svg?branch=master)](https://travis-ci.org/vshesh/glue)
[![Coverage Status](https://coveralls.io/repos/github/vshesh/glue/badge.svg?branch=master)](https://coveralls.io/github/vshesh/glue?branch=master)

## Quickstart

```bash
$ git clone <this repo>
$ python3
>>> import glue
>>> reg = glue.Registry(glue.elements.Bold, glue.elements.Italic, glue.elements.Paragraphs)
>>> glue.parse(reg, glue.elements.Paragraphs, '*test*')
<div><p><strong>text</strong></p></div>
```

## Dream

### Web

fully extensible text, with custom react-components, and even forms!

```md
# Title

blah blah blah T[some text](tooltip!)

![alt](img url)

---mermaid
graph TD
A --> B
B --> C
C --> A
...

---katex
\sum_{k=0}^x \binom{x}{k} = 2^x
...

---annotated-image http://img.url/goes/here
5,6: Note the brush strokes here!
100,100: woohoo the end of the image!
...

---sidebyside
[link](goes here) | other column
---code python    | ---code julia
def f(x):         | function f(x)
  return 2*x      |  2x
                  | end
... | ...
...

---react-yaml ComponentName
prop1: [data, more, data]
prop2:
  x: 1
  y: 2
...


---form
Name: [text]
Age: [number]
Descr:
[textarea]
[checkbox] Agree to Terms
...
note how i put more blocks in the columns! and how it doesn't need to line up!
That's the power of nesting!
```

### Seamless Code/Docs (a la Rusthon/Mathematica Notebook/Jupyter)

```md
# Hilbert Curves for Rectangles

## L System

here, we'd like to be able to generate some order of an l system.
For that, we need to be able to replace the text easily, and we need to
replace many tokens at the same time:

---code python
def multireplace(rep, text):
  """
  Takes
  """
  r = dict((re.escape(k), v) for k, v in rep.items())
  pattern = re.compile("|".join(r.keys()))
  return pattern.sub(lambda m: r[re.escape(m.group(0))], text)
...

Now, functions that correspond to the hilbert curve.
---code python
def hilbert(order):
  s = 'L'
  for i in range(order):
    s = multireplace({'L':'+RF-LFL-FR+', 'R':'-LF+RFR+FL-'}, s)
  return re.sub(r'[LR]|(?:\+-)|(?:-\+)', '', s)

def movements(hilbert):
  plus = {'U': 'L', 'L': 'D', 'D': 'R', 'R': 'U'}
  minus = {'U': 'R', 'R': 'D', 'D': 'L', 'L': 'U'}
  
  m = []
  d = 'R'
  for e in hilbert.split('F'):
    n = d if e == '' else (plus if e == '+' else minus)[d]
    m.append((d, n))
    d = n
  return m
...

The movements gives us an array of the corners. Let's see if this maps
nicely onto a larger pattern or not!.

There's some mapping that requires us to think about how to flip the
original left and up patterns.

```

### Journal

```md
# 2015-05-02

Some free text about my experience of the morning.
I had cereal for breakfast. Again. I'm just too lazy to cook oatmeal.

## 12-1pm Lunch w/Nick at Lag
I had lunch with nick!
it was nice lunch too - we had this really good mexican food.

## 2-4pm Presentation for Class at 550 w/Sarah
The presentation went well...
@John was there too! I was surprised to see him.

!(/url/to/img)

etc
```

## Overview

This is a parser framework that specifically designed for plain-text.

At the risk of [that famous XKCD comic](https://xkcd.com/927/), I wrote this
small API for a parser-generator for plain-text based on regexes. Regexes can be
eeeeew, but they're a lot better than a lot of other things, and they seem
to be pretty standard across many parser applications (eg, syntax highlighters).
In order to remove *some* regex pain, I've written generators that will
help you write simple patterns that I imagine you will want to use.
Make sure that you `pip install regex` and use that library. It will eventually
become the real regex library, but it has a lot of features that are useful
(especially `\K`).

You need to design yourself something I'm calling a **registry**.
What's that, you ask? It's just a list of **elements**, which can be `block`
or `inline` style elements. `block` and `inline` correspond to the html idea of
`display` and `block` elements are expected to look like `div`s
in html and `inline` elements are expected to look like `span` elements.

Ok, so what is an **element**?

### Inline Elements

Inline elements consist of

* `name` the name of the element - should be in dash-case, like `critic-add`
* `nest` how to nest other inline elements (explained in the next section)
* `subscribe`
* `escape`
* `parser` takes the form `[(regex, parser_fn), (regex, parser_fn)]`.
  * `parser_fn(groups) -> ['span', {'attr': 'value'}, 'something']`
    * takes the captured groups from the regex and returns html.
    * or in the case of `nest=FRAME`, takes an html body and returns more html.
  * TODO in the future, i'd like to decouple the generation from the insertion
    so you can reduce over all the matches in the document.
    However, it's completely unclear how that's supposed to work when you
    can guarantee nothing about nested components - any one of them can change
    what's generated beneath them however they like.
    
Inline elements can mostly be written in the functional form, since the parser
functions can be expressed with lambdas. However, there is a decorator
for the situation in which you have just one regex and one accompanied parser.
Unfortunately, decorators are a very limited form of macros.

```python
# one regex example - (note, Italic is much better represented with
# IdenticalInlineFrame('italic', '_', 'em') - this is actually boilerplate).
@inlineone(r'(?<!\\)(?:\\\\)*\K_(.*?(?<!\\)(?:\\\\)*)_')
def Italic(groups):
  return ['em', groups[0]]

# function style
Italic = Inline('italic', Nesting.FRAME, ['all'], '_',
  [(re.compile(r'(?<!\\)(?:\\\\)*\K_(.*?(?<!\\)(?:\\\\)*)_'),
    lambda groups: ['em', groups[0]])])
```

### Block Elements

Block elements consist of:

* `name` the name of the element - should be in dash-case, like `block-name`
* `nest` how to nest other blocks
* `nesti` how to nest inline elements (currently does nothing, `nest` is
  used in both places, but this is left here in case there's a day someone
  needs separate nesting policies for inline/block elements).
* `subblock` what other block elements are legal inside this block element.
  * `inherit` is a special keyword here, that inherits from the parent.
  * `all` is a special keyword that subscribes to ALL block elements in the registry.
* `subinline` what other inline elements are legal inside this block element.
  * `inherit` is a special keyword here, that inherits from the parent.
  * `all` is a special keyword that subscribes to ALL block elements in the registry.
* `parser(text) -> ['div', ['p', ...]]` a parser function that returns a list
  form of html that can be parsed by the library [cottonmouth](https://github.com/nosamanuel/cottonmouth).
  * note: I ported cottonmouth to python3 and then added the ability to define
    attributes that are dictionaries that will be made into style like elements.
    So `['div', {'attr': {'x':'y'}}]` becomes `<div attr="x:y;">`. It is
    particularly useful when trying to define inline css on the returned elements.
    
I recommend using the decorator I wrote to write these, since the block parser
functions tend not to be trivial, but you can do it function style, too.

```python
# decorator style
@block()
def Paragraphs(text):
  """Very simple paragraphs component that renders blocks of text with
  line break in the middle (\\n\\n) as separate <p></p> elements.
  """
  return ['div', *map(lambda x: ['p', x.strip()], text.split('\n\n'))]

# function style
def paragraphs_parser(text):
  """Very simple paragraphs component that renders blocks of text with
  line break in the middle (\\n\\n) as separate <p></p> elements.
  """
  return ['div', *map(lambda x: ['p', x.strip()], text.split('\n\n'))]

Paragraphs = Block('paragraphs', Nesting.POST, Nesting.POST,
                   ['all'], ['all'], paragraphs_parser)
```

You can see how the decorator style is easier, since it auto-calculates the
name, gives you sane defaults for the nesting,
and doesn't require you to think up *another* name for the parser.
Still, option exists, and is useful for writing functions that generate `Block`s.

### Registry

Then, you make a registry out of the elements you've defined, and parse!

```python
from glue.registry import Registry
from glue import parser
reg = Registry(Italic, Paragraphs)
text = '''
_italic text_ text

a new paragraph! _more italic text_ \_ <- escaped underscore.
'''
parser(reg, Paragraphs, text)
# <html output here>
```

## Motivation

There are excellent full CFG parsers, and there are great plaintext parsers
if you're willing to pick a dialect and stick to it, but there's no real way to
extend the parsers yourself or add more block types etc. What has happened as
a result is that we have tons of minutely different dialects and sects of major
text-document writing styles (see: myriad Markdown versions, reStructuredText,
pandoc, etc). In order to add extra types of plain-text formats that don't have
anything to do with the original parser (eg: KaTeX or Mermaid), you either have
to extend the original parser somehow (and either deal with custom ASTs or formats)
or make peace with raw html and loading a script into the page that will search
the page and parse based on classes etc (this might still have to be done).

Take, for example, CriticMarkup. Someone wrote a spec for this, but it's been
implemented in some Markdown parsers and not others, so maybe it's there and
it's great! Or maybe you want it, but you can't have it (sad face). Do you
switch dialects? Does it have all the other features? Maybe write a Pandoc
filter?

It's pretty simple to add CriticMarkup to a registry using **Glue**:

```python
CriticAdd = MirrorInlineFrame('critic-add', '{++', 'ins')
CriticDel = MirrorInlineFrame('critic-del', '{--', 'del')
CriticComment = MirrorInlineFrame('critic-comment', '{>>', 'span.critic.comment')
CriticHighlight = MirrorInlineFrame('critic-highlight', '{==', 'mark')

CriticMarkdown = Registry(CriticAdd, CriticDel, CriticComment, CriticHighlight)
```

I'll leave CriticSub as an exercise for the reader. It fits in a similar vein
as the Link component. There is an example section that discusses some
common architectures of these components and how they could fit together.

`MirrorInlineFrame` is a helper function I provide for you, which is written
to simply writing a parser for an element with one group in which the start
and end pattern are mirrors of each other - I've defined the start pattern, and
the function will compute the other side eg `++}` and then make the appropriate
regex.

This is so simple, in fact, that I went ahead and included it for you.

## Examples/Common Architectures

TODO
