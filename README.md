# Glue: plain-text format for other plain-text formats

[![Build Status](https://travis-ci.org/vshesh/glue.svg?branch=master)](https://travis-ci.org/vshesh/glue)
[![Coverage Status](https://coveralls.io/repos/github/vshesh/glue/badge.svg?branch=master)](https://coveralls.io/github/vshesh/glue?branch=master)

## Quickstart

```bash
$ git clone <this repo>
$ cd glue
glue$ echo '*test*' | python3 -m glue 


$ python3
>>> import glue
>>> from glue.library import Standard
>>> glue.parse(Standard, '*test*')
<div><p><strong>text</strong></p></div>

>>> import glue.elements
>>> reg = glue.Registry(glue.elements.Bold, glue.elements.Italic, glue.elements.Paragraphs)
>>> glue.parse(reg, glue.elements.Paragraphs, '*test*')
<div><p><strong>text</strong></p></div>
```

## Dream

Really flexible plain-text syntaxes that can be used to create any kind
of rich content. Also a way to extend this language over time so you can
continually improve the ability to express yourself.

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
note how i put more blocks in the columns! and how it doesn't need to line up!

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
help you write simple patterns that I imagine you will want to use. My
thinking is that these patterns account for a majority of the use cases
you will hopefully want. 
Make sure that you `pip install regex` and use that library. It will eventually
become the real regex library, but it has a lot of features that are useful
(especially `\K`). It's required for running glue anyway, so you might 
as well take advantage of it.

## How To Use

### Use case 1: Parse some text.

For those who are raring to go - this library comes prebundled with a 
'standard library' of sorts which has the rudimentary components you may
want to use. Here are the inline syntaxes included in the `Standard` registry:

* `*text*` -> **text**
* `_text_` -> _text_
* ```text``` -> `text`
* `__text__` -> underlined text
* `~text~` -> strikethrough text
* all of [critic markup](http://criticmarkup.com/) (`{++ins++}`, `{--sub--}`, `{==mark==}` etc)
* `T[text](tooltip)` -> quick n dirty inline tooltip (missing CSS right now)
* `# header` -> a la markdown header
* `![img](url)` -> img like markdown, sized to max-width 100% so that it doesn't look ridiculous.

There are also block elements, like math from `Katex`, code block 
highlighting from `highlight.js`, and side-by-side column support. 
To invoke a block, use the YAML document syntax like so:

```yaml
---name
body of the block goes here...
...
```

Some blocks take options, like a command line:

```yaml
---code python
print('Hello World')
...
```

Woot, now you can have a code sample in your document!

To do the parsing, just run `cat file | python3 -m glue` to see html
be spit out. Append this html to a file with the proper assets included
(see static/index.html) and everything should work fine. In a future 
version, assets will be autogenerated and standalone html file will be 
completely automatic.

Full documentation for the components that come bundled with glue are
forthcoming, but for now you can read the library.py file to see the 
details.

## Use Case 2: Customize a registry

Glue operates by parsing text using a bag of `Element`s called a 
`Registry`. 

What's that, you ask? It's just a list of `Element`s, which can be `block`
or `inline` style elements. `block` and `inline` correspond to the html idea of
`display` and `block` elements are expected to look like `div`s
in html and `inline` elements are expected to look like `span`s. More on
this in use case 3, which is writing your own component.

You can freely add and subtract elements from Registries. Let's say
I want to add an audio element to the `Standard` registry:

```python
from glue.library import Standard, Italic
MyRegistry = Standard + [Audio]
# OR
MyRegistry = copy.copy(Standard)
MyRegistry -= Italic
```

Addition reads from any iterable and adds the elements in it one at a time
in order. 

Similarly I can subtract an iterable. Let's say I don't want to have 
italic text in my registry. I can just remove it like so:

```python
from glue.library import Standard, Italic
MyRegistry = Standard - [Italic]
# OR
MyRegistry = copy.copy(Standard)
MyRegistry -= [Italic]
```

I can also modify properties of an element, say, its name:

```python
MyRegistry |= {'monospace': {'name': 'mono'}}
```

Finally, I can merge the registries together. Here's a line from library.py
that does just that:

```python
Standard = Registry(Paragraphs, top=Paragraphs) | StandardInline | CriticMarkup
```

Internally, they're just `OrderedDicts` with a few extra bells and whistles.
One quick note about `top` -> this is the elemnt that forms the "outer context"
of the file, and it's the implicit block that the file is wrapped in before
parsing.

## Use Case 3: Write a new component


### Elements

Elements in Glue are defined by four properties - 

* `name` the name of the element - should be in dash-case, like `critic-add`
  * for sanity, the name is autogenerated from the name of the parser function.
    you should not try to generate it yourself.
* `nest` Nesting policy - defines in which order internal elements are parsed - either 
  before (SUB), after (POST), or not at all.
* `sub` names of other inline elements allowed inside this one. Can also put
  `'all'` if you would like to allow every element. This is the default. 
* `parser` - function that takes the body text and returns the HTML 
  in the form of the python `cottonmouth` library.

### Inline Elements

Inline elements are a subclass of elements that are intended to wrap
text inline. Think `span` in HTML, or bold/italic/underline from MS Word.
Along with the above, they also have:

* `escape` characters that should be escaped in the block body text.
* `parser(groups) -> ['span', {'attr': 'value'}, 'something']`
    * takes the captured groups from the regex and returns html.
    * or in the case of `nest=FRAME`, takes an html body and returns more html.
 
 Here is an example `Inline` element for italic text a la Markdown. Note
 how much easier the decorator version is. In general, use the helper 
 decorators and functions! It will save you a lot of raw regex writing.

```python
# one regex example - (note, Italic is much better represented with
# IdenticalInlineFrame('italic', '_', 'em') - this is clunky).
@inlineone(r'(?<!\\)(?:\\\\)*\K_(.*?(?<!\\)(?:\\\\)*)_')
def Italic(groups):
  return ['em', groups[0]]

# function style
Italic = Inline('italic', Nesting.FRAME, ['all'], '_', 
    re.compile(r'(?<!\\)(?:\\\\)*\K_(.*?(?<!\\)(?:\\\\)*)_'),
    lambda groups: ['em', groups[0]])
```



### Block Elements

Block elements look like elements with:
* `opts`: a string passed to getopts that states which flags are allowed
  as kwargs options for this block. (eg, language for code block).

    I recommend using the decorator to write these, since the block parser
functions tend not to be trivial, but you can do it function style, too.

```python
# decorator style
@block() # you can override defaults eg: @block(nest=Nest.SUB)
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

Paragraphs = Block(name='paragraphs', nest=Nesting.POST, sub=['all'], parser=paragraphs_parser)
```

You can see how the decorator style is easier, since it auto-computes the
name, gives you sane defaults for the nesting,
and doesn't require you to think up *another* name for the parser.
Still, the raw option exists, and is useful for writing functions that 
generate `Block`s, such as in elements.py.

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
to extend the original parser somehow (and deal with custom ASTs or formats)
or make peace with raw html and loading a script into the page that will search
the page and parse based on classes etc (eg, katex).

Take, for example, CriticMarkup. Someone wrote a spec for this, but it's been
implemented in some Markdown parsers and not others, so maybe it's there and
it's great! Or maybe you want it, but you can't have it (sad face). Do you
switch dialects? Does it have all the other features? Maybe write a Pandoc
filter?

It's pretty simple to add CriticMarkup to a registry using **Glue**:

```python
CriticAdd = MirrorInline('critic-add', '{++', 'ins')
CriticDel = MirrorInline('critic-del', '{--', 'del')
CriticComment = MirrorInline('critic-comment', '{>>', 'span.critic.comment')
CriticHighlight = MirrorInline('critic-highlight', '{==', 'mark')

CriticMarkdown = Registry(CriticAdd, CriticDel, CriticComment, CriticHighlight)
```

I'll leave CriticSub as an exercise for the reader. It fits in a similar vein
as the Link component. It's been implemented in the library.py file if 
you want an answer as to how it looks.

Note: `MirrorInline` is a helper function I provide, which is written
to simply writing a parser for an element with one group in which the start
and end pattern are mirrors of each other - I've defined the start pattern, and
the function will compute the other side eg `++}` and then make the appropriate
regex. There are many such functions available as part of the parser, and
they *significantly* improve the life of the developer. Please take a 
look at them. More explanation/documentation will come soon.

## Examples/Common Architectures

TODO
