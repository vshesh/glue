# from cottonmouth library, ported to python3 by Vishesh Gupta.
# also, added the ability to define style-type tags using the css syntax, so
# a dictionary value for an attribute is converted to: "key:value;key2:value2;"

import collections
import itertools

HTML_VOID_TAGS = [
    'area',
    'base',
    'br',
    'col',
    'command',
    'embed',
    'hr',
    'img',
    'input',
    'keygen',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr',
]

# NEVER USED!
HTML_TAGS = [
    'a',
    'address',
    'applet',
    'area',
    'article',
    'aside',
    'b',
    'base',
    'basefont',
    'bgsound',
    'big',
    'blockquote',
    'body',
    'br',
    'button',
    'caption',
    'center',
    'code',
    'col',
    'colgroup',
    'command',
    'dd',
    'details',
    'dir',
    'div',
    'dl',
    'dt',
    'em',
    'embed',
    'fieldset',
    'figure',
    'font',
    'footer',
    'form',
    'frame',
    'frameset',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'head',
    'header',
    'hr',
    'html',
    'i',
    'iframe',
    'image',
    'img',
    'input',
    'isindex',
    'li',
    'link',
    'listing',
    'marquee',
    'menu',
    'meta',
    'nav',
    'nobr',
    'noembed',
    'noframes',
    'noscript',
    'object',
    'ol',
    'p',
    'param',
    'plaintext',
    'pre',
    's',
    'script',
    'section',
    'select',
    'small',
    'source',
    'strike',
    'strong',
    'style',
    'table',
    'tbody',
    'td',
    'textarea',
    'tfoot',
    'th',
    'thead',
    'title',
    'tr',
    'track',
    'tt',
    'u',
    'ul',
    'wbr',
    'xmp',
]

def render(*content, **context):
    """
    Renders a sequence of content as HTML.
    """
    return ''.join((e for c in content for e in render_content(c, **context)))


def render_content(content, **context):
    """
    Renders Python data as HTML.
    Content can be one of the following:
      - A string containing raw HTML, rendered as-is
      - A callable that will be called with the current **context
      - A sequence beginning with a literal HTML tag name
      - Any other value, coerced to unicode
    """
    if content is None:
        yield ''
    elif isinstance(content, str):
        yield content
    elif isinstance(content, collections.Callable):
        for e in render_content(content(**context), **context):
            yield e
    elif isinstance(content, collections.Iterable):
        for e in render_iterable(content, **context):
            yield e
    else:
        yield str(content)


def render_iterable(content, **context):
    """
    Renders a list, tuple, or generator of content as HTML.
    """
    tail = iter(content)
    head = next(tail)

    # Render tag around the content
    if isinstance(head, str):
        for e in render_tag(head, tail, **context):
            yield e
    # Render nested lists
    elif isinstance(head, collections.Iterable):
        for e in render_iterable(head, **context):
            yield e
        for content in tail:
            for e in render_content(content, **context):
                yield e


def render_tag(tag, content, **context):
    """
    Renders an HTML tag with its content.
    """
    try:
        # Parse extra attributes and remainder
        content, remainder = itertools.tee(content)
        extra = dict(**next(remainder))
    except StopIteration:
        # If there is no remainder, we just render the tag
        extra, remainder = {}, []
    except TypeError:
        # If the
        extra, remainder = {}, content

    # Default to div if no explicit tag is provided
    if tag.startswith('#'):
        tag = 'div{}'.format(tag)

    # Split tag into ["tag#id", "class1", "class2", ...] chunks
    chunks = tag.split('.')

    # Parse tag and id out of tag shortcut
    tag = chunks[0]
    if '#' in chunks[0]:
        tag, extra['id'] = chunks[0].split('#')

    # Format classes
    classes = extra.get('class', [])
    classes.extend(chunks[1:])
    if classes:
        extra['class'] = ' '.join(classes)

    def dictattr(d):
      return ''.join('{}:{};'.format(*x) for x in d.items())
    # Format attributes
    attributes = ''.join(' {}="{}"'.format(i[0],
                                           dictattr(i[1])
                                           if isinstance(i[1], dict)
                                           else i[1])
                         for i in list(extra.items()))

    # Start our tag sandwich
    yield '<{}{}>'.format(tag, attributes)

    # Render the delicious filling or toppings
    for content in remainder:
        for e in render_content(content, **context):
            yield e

    # CLOSE THE TAG IF WE HAVE TO I GUESS
    if tag not in HTML_VOID_TAGS:
        yield '</{}>'.format(tag)
