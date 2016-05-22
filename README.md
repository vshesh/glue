# Glue, plain-text format for other plain text-formats

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

## Overview

This is a parser framework that specifically designed for plain-text.
There are excellent full CFG parsers, and there are great plaintext parsers
if you're willing to pick a dialect and stick to it, but there's no real way to
extend the parsers yourself or add more block types etc. What has happened as
a result is that we have tons of minutely different dialects and sects of major
text-document writing styles (see: myriad Markdown versions, reStructuredText,
pandoc, MS Word etc), or through some combination of raw html and js scripts,
you can plug in special formats (eg, KaTeX or Mermaidjs). Now we even have
programs designed to interoperate between these different formats as well.

At the risk of [that famous XKCD comic](https://xkcd.com/927/)

You need to design yourself something I'm calling a **registry**.
What's that, you ask? It's just of **elements**, which can be either `block`
or `inline` style elements. `block` and `inline` correspond to the html idea of
`display: block|inline` and `block` elements are expected to look like `div`s
in html and `inline` elements are expected to look like `span` elements.

Ok, so what is an **element**?

### Block Elements

Block elements are defined as
