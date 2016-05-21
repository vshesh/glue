

def makeregistry(*args: Union[Block, Inline]):
  return dict((x.name, x) for x in args)

registry = makeregistry(Bold, Italic, Monospace, Underline, Link,
                        NoopBlock, Paragraphs, SubTestBlock)
