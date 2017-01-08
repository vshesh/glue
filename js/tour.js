var Tour = {
    view: function() {
      return m('div', m('h1', 'A Tour of the Standard Registry'), m('p', 'This document is a primer for how to use ', m('strong', {}, 'GLUE'), ', and also a tour of the various components that come prebundled in the ', m('code', {}, 'library.py'), ' file.'), m('p', "If you're interested in reading about how to ", m('strong', {}, 'write'), ' glue components, as opposed to how to use them, then go look at ', m('a', {'href': '/examples/anatomy_of_a_component'}, '"Anatomy of a Component"'), ' and ', m('a', {'href': '/examples/a_history_of_the_standard_registry'}, '"A History of the Standard Registry"'), ' which describe what went into making the components that are displayed here, and teaches strategies for how you can implement your own in the simplest way possible. Hopefully it covers about 80% of the cases that you would be interested in.'), m('h2', 'Basic Editing'), m('p', "Basic editing encompasses things you'd normally like to do in any editing environment, which are things like: ", m('strong', {}, 'bold'), ', ', m('em', {}, 'italic'), ', ', m('code', {}, 'monospace'), ', ', m('del', {}, 'strikethrough'), ', ', m('span', {'style': 'text-decoration:underline;'}, 'underline'), ' and so on.\nSince these basic editing elements are used so often, there is a simple way to make each of them:'), m('table.matrix.matrix-table', m('tr', {'style': {}}, m('td', {}, m('span', {'style': 'text-decoration:underline;'}, m('strong', {}, 'What you want'))), m('td', {}, m('span', {'style': 'text-decoration:underline;'}, m('strong', {}, 'What you type'))), m('td', {}, m('span', {'style': 'text-decoration:underline;'}, m('strong', {}, 'What you get')))), m('tr', {'style': {}}, m('td', {}, 'bold text'), m('td', {}, m('code', {}, '*text*')), m('td', {}, m('strong', {}, 'text'))), m('tr', {'style': {}}, m('td', {}, 'italic text'), m('td', {}, m('code', {}, '_text_')), m('td', {}, m('em', {}, 'text'))), m('tr', {'style': {}}, m('td', {}, 'monospace text '), m('td', {}, m('code', {}, '`text`')), m('td', {}, m('code', {}, 'text'))), m('tr', {'style': {}}, m('td', {}, 'underline text '), m('td', {}, m('code', {}, '__text__')), m('td', {}, m('span', {'style': 'text-decoration:underline;'}, 'text'))), m('tr', {'style': {}}, m('td', {}, 'strikethrough text'), m('td', {}, m('code', {}, '~text~')), m('td', {}, m('del', {}, 'text'))), m('tr', {'style': {}}, m('td', {}, 'hyperlink'), m('td', {}, m('code', {}, '[link](http://google.com)')), m('td', {}, m('a', {'href': 'http://google.com'}, 'link'))), m('tr', {'style': {}}, m('td', {}, 'tooltip'), m('td', {}, m('code', {}, 'T[text](tooltip)')), m('td', {}, m('span.tooltip', 'text', m('div.tooltip-text', 'tooltip')))), m('tr', {'style': {}}, m('td', {}, m('a', {'href': 'https://criticmarkup.com'}, 'critic markup'), ' insert text'), m('td', {}, m('code', {}, '{++inserting text++}')), m('td', {}, m('ins', {}, 'inserting text'))), m('tr', {'style': {}}, m('td', {}, m('a', {'href': 'https://criticmarkup.com'}, 'critic markup'), ' delete text'), m('td', {}, m('code', {}, '{--deleting text--}')), m('td', {}, m('del', {}, 'deleting text'))), m('tr', {'style': {}}, m('td', {}, m('a', {'href': 'https://criticmarkup.com'}, 'critic markup'), ' highlight text'), m('td', {}, m('code', {}, '{==highlighted text==}')), m('td', {}, m('mark', {}, 'highlighted text'))), m('tr', {'style': {}}, m('td', {}, m('a', {'href': 'https://criticmarkup.com'}, 'critic markup'), ' replace text'), m('td', {}, m('code', {}, '{~~old~>new~~} text')), m('td', {}, [m('del', 'old'),m('ins', 'new')], ' text')), m('tr', {'style': {}}, m('td', {}, 'header (more ', m('code', {}, '#'), ' gives smaller header)'), m('td', {}, m('code', {}, '#header'), ', ', m('code', {}, '##header'), ', ', m('code', {}, '###header'), ', so on'), m('td', {}, m('h1', 'header'))), m('tr', {'style': {}}, m('td', {}, 'inline image'), m('td', {}, m('code', {}, '!![image](http://lorempixel.com/50/50)')), m('td', {}, m('img', {'style': {'max-width': '100%', 'display': 'inline-block', 'vertical-align': 'middle'}, 'src': 'http://lorempixel.com/50/50', 'alt': 'image'}))), m('tr', {'style': {}}, m('td', {}))), m('h3', 'A note about escapes (when you want a literal character)'), m('p', 'Sometimes you really want an actual asterisk, as opposed to a bold element. What do you do then? Type ', m('code', {}, '\\*'), ' in your document, like so: *. This will make a literal asterisk in the final result. Putting a backslash in front of any character will cause it to lose any special meaning it has.'), m('p', 'The same principle applies to literal underscores (', m('code', {}, '\\_'), '), tildes (', m('code', {}, '\\~'), '), and backticks (', m('code', {}, '\\`'), '). And, of course, backslashes themselves (', m('code', {}, '\\\\'), ').'), m('p', 'You may also want a literal bold asterisk. To make one, type ', m('code', {}, '*\\**'), ' in the document (an escaped asterisk inside two asterisks to make it bold). It renders like this: ', m('strong', {}, '*'), " versus *. This isn't a special case, but since it can be a bit confusing, I've left it here."), m('p', 'Another option is that you may want to escape a link, for example, to explain to someone how to make a link! To do this, prefix the link with ', m('code', {}, '\\'), ', like so: ', m('code', {}, '\\[link](google.com)'), ' -> [link](google.com). The ', m('code', {}, '['), ' character loses its special meaning so the link is not processed.'), m('h2', 'Environments'), m('p', 'Environments allow you to create other things than paragraphs of text. Here is an example of an environment - a list:'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('ul', m('li', 'first item'), m('li', 'second item'))), m('div', {'style': {'flex': 1}}, m('pre', m('code#371d5214-41e0-4b7d-b0f8-fd1aa4eb68c4.language-md', '---list\nfirst item\nsecond item\n...\n'), m('script', {'key': '371d5214-41e0-4b7d-b0f8-fd1aa4eb68c4'}, "hljs.highlightBlock(document.getElementById('371d5214-41e0-4b7d-b0f8-fd1aa4eb68c4'))")))), m('p', '\nEvery environment starts with three dashes (', m('code', {}, '---'), ') and ends with three dots (', m('code', {}, '...'), '). The name of the environment goes right after the three dashes.'), m('p', 'You will always see the rendered version on the left and the code to make it happen on the right in the following examples.'), m('h3', 'Blockquote'), m('p', 'A ', m('code', {}, 'Blockquote'), ' is nothing more than a piece of text made to stand out. Normally this is done with some indentation and larger font:'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('div.blockquote', m('p', "Hi I'm a blockquote"))), m('div', {'style': {'flex': 1}}, m('pre', m('code#5f22c0d3-dcbf-4140-abe0-9c56891524af.language-md', "---blockquote\nHi I'm a blockquote\n...\n"), m('script', {'key': '5f22c0d3-dcbf-4140-abe0-9c56891524af'}, "hljs.highlightBlock(document.getElementById('5f22c0d3-dcbf-4140-abe0-9c56891524af'))")))), m('p', '\nYou can also put other things into the blockquote like a list:'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('div.blockquote', m('ul', m('li', 'first item'), m('li', 'second item')))), m('div', {'style': {'flex': 1}}, m('pre', m('code#7c15e1c8-ff25-4e73-9070-afa6c26f9ed8.language-md', '---blockquote\n---list\nfirst item\nsecond item\n...\n...\n'), m('script', {'key': '7c15e1c8-ff25-4e73-9070-afa6c26f9ed8'}, "hljs.highlightBlock(document.getElementById('7c15e1c8-ff25-4e73-9070-afa6c26f9ed8'))")))), m('p'), m('h3', 'List'), m('p', 'List is pretty self-explanatory.'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('ul', m('li', 'first item'), m('li', 'second item', m('ul', m('li', 'sub item 1'), m('li', 'sub item 2'))), m('li', 'third item'))), m('div', {'style': {'flex': 1}}, m('pre', m('code#0b02007c-d118-472c-8fd9-e6aab3741989.language-md', '---list\nfirst item\nsecond item\n  sub item 1\n  sub item 2\nthird item\n...\n'), m('script', {'key': '0b02007c-d118-472c-8fd9-e6aab3741989'}, "hljs.highlightBlock(document.getElementById('0b02007c-d118-472c-8fd9-e6aab3741989'))")))), m('p', '\nPut each item one at a time on a line. If you want to have a sub item, indent the line any amount more than the previous line and it will be a sub item.'), m('p', 'One more thing may be that you want an ', m('strong', {}, 'ordered'), ' list. You can achieve that with the ', m('code', {}, '-o'), ' option:'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('ol', m('li', 'first item'), m('li', 'second item', m('ol', m('li', 'sub item 1'), m('li', 'sub item 2'))), m('li', 'third item'))), m('div', {'style': {'flex': 1}}, m('pre', m('code#a6f2ef51-c313-4db9-a7de-ad4a8d60b934.language-md', '---list -o\nfirst item\nsecond item\n  sub item 1\n  sub item 2\nthird item\n...\n'), m('script', {'key': 'a6f2ef51-c313-4db9-a7de-ad4a8d60b934'}, "hljs.highlightBlock(document.getElementById('a6f2ef51-c313-4db9-a7de-ad4a8d60b934'))")))), m('p'), m('h3', 'SideBySide'), m('p', 'This environment allows you to have multi-columns in your document:'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('div', {'style': {'display': 'flex'}}, m('div', {'style': {'flex': '1'}}, 'a\nfoo'), m('div', {'style': {'flex': '1'}}, 'b\nbar'), m('div', {'style': {'flex': '1'}}, 'c\nbaz'))), m('div', {'style': {'flex': 1}}, m('pre', m('code#4f580175-cba5-42b9-920b-4fe36d936f99.language-md', '---side-by-side\na | b | c\nfoo | bar | baz\n...\n'), m('script', {'key': '4f580175-cba5-42b9-920b-4fe36d936f99'}, "hljs.highlightBlock(document.getElementById('4f580175-cba5-42b9-920b-4fe36d936f99'))")))), m('p', '\nNote how the text in the columns is processed as one contiguous section rather than distinct rows. This allows you to also put other environments inside the column:'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('div', {'style': {'display': 'flex'}}, m('div', {'style': {'flex': '1'}}, m('ul', m('li', 'item 1'), m('li', 'item 2'))), m('div', {'style': {'flex': '1'}}, 'b\n\n\nbar'), m('div', {'style': {'flex': '1'}}, 'c\n\n\nbaz'))), m('div', {'style': {'flex': 1}}, m('pre', m('code#58d0ba3b-8b75-4ebe-9745-7ef889fc093f.language-md', '---side-by-side\n---list | b | c\nitem 1 |\nitem 2 |\n... | bar | baz\n...\n'), m('script', {'key': '58d0ba3b-8b75-4ebe-9745-7ef889fc093f'}, "hljs.highlightBlock(document.getElementById('58d0ba3b-8b75-4ebe-9745-7ef889fc093f'))")))), m('p', '\nNote how there are empty pipes on the rows with the items, even though there is nothing corresponding in the other columns. This is necessary to know which column to put ', m('code', {}, 'item 1'), ' and ', m('code', {}, 'item 2'), ' in.'), m('h3', 'Matrix'), m('p', m('code', {}, 'Matrix'), ' is similar to ', m('code', {}, 'SideBySide'), ', but each row is processed separately.'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('div.matrix.matrix-flex', m('div', {'style': {'display': 'flex'}}, m('span', {'style': {'flex': 1}}, 'a'), m('span', {'style': {'flex': 1}}, 'b'), m('span', {'style': {'flex': 1}}, 'c')), m('div', {'style': {'display': 'flex'}}, m('span', {'style': {'flex': 1}}, 'x'), m('span', {'style': {'flex': 1}}, 'y'), m('span', {'style': {'flex': 1}}, 'z')), m('div', {'style': {'display': 'flex'}}, m('span', {'style': {'flex': 1}})))), m('div', {'style': {'flex': 1}}, m('pre', m('code#edcdc2f6-c2b9-4b58-8dc6-97af0c027ded.language-md', '---matrix\na | b | c\nx | y | z\n...\n'), m('script', {'key': 'edcdc2f6-c2b9-4b58-8dc6-97af0c027ded'}, "hljs.highlightBlock(document.getElementById('edcdc2f6-c2b9-4b58-8dc6-97af0c027ded'))")))), m('p', "\nThe matrix is defaulted to have equal width columns, but if you'd like for the columns to be sized based on the width of its contents, you can ask the matrix to render as a table:"), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('table.matrix.matrix-table', m('tr', {'style': {}}, m('td', {}, '23'), m('td', {}, '13109'), m('td', {}, '11-0230124-0193')), m('tr', {'style': {}}, m('td', {}, '24'), m('td', {}, '12318'), m('td', {}, '13pi110-29-0-12')), m('tr', {'style': {}}, m('td', {})))), m('div', {'style': {'flex': 1}}, m('pre', m('code#3f6a07aa-03da-443b-bf65-1e11010aa954.language-md', '---matrix table\n23 | 13109 | 11-0230124-0193\n24 | 12318 | 13pi110-29-0-12\n...\n'), m('script', {'key': '3f6a07aa-03da-443b-bf65-1e11010aa954'}, "hljs.highlightBlock(document.getElementById('3f6a07aa-03da-443b-bf65-1e11010aa954'))")))), m('p', '\nNow you see that the columns with more data are wider, and the ones with less are smaller.'), m('h3', 'CodeBySide'), m('p', "I've been using this environment to show off the other environments, so I've included it here in case you want to use it to show off examples of your own."), m('p', 'The ', m('code', {}, 'CodeBySide'), " environment will show the text inside the environment next to a rendered version of what's there so that you can simultaneously see what to type and what you get."), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('ul', m('li', 'first item'), m('li', 'second item'))), m('div', {'style': {'flex': 1}}, m('pre', m('code#9aa55cc1-ec66-46ad-88cc-970139e327cf.language-md', '---list\nfirst item\nsecond item\n...\n'), m('script', {'key': '9aa55cc1-ec66-46ad-88cc-970139e327cf'}, "hljs.highlightBlock(document.getElementById('9aa55cc1-ec66-46ad-88cc-970139e327cf'))"))))), m('div', {'style': {'flex': 1}}, m('pre', m('code#41e1de98-8abb-4d6d-a20a-ff8b6434ad13.language-md', '---code-by-side\n---list\nfirst item\nsecond item\n...\n...\n'), m('script', {'key': '41e1de98-8abb-4d6d-a20a-ff8b6434ad13'}, "hljs.highlightBlock(document.getElementById('41e1de98-8abb-4d6d-a20a-ff8b6434ad13'))")))), m('p', '\nThis layout may be rather confusing - but the right half is the code required to make the left half. In the left half, there is a ', m('code', {}, 'CodeBySide'), ' element, which is showing you how to make a list.'), m('p', 'In general, if you wrap anything in the ', m('code', {}, 'CodeBySide'), ' environment, you will see the code required to make it on the right (it will match whatever is inside the environment).'), m('h2', 'Media'), m('p'), m('h3', 'Audio'), m('p', 'Simple audio elements can be added inline with ', m('code', {}, '@[url]')), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, '@[http://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3]\n'), m('div', {'style': {'flex': 1}}, m('pre', m('code#612f6924-9d90-4036-a23b-27de7a008c27.language-md', '@[http://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3]\n'), m('script', {'key': '612f6924-9d90-4036-a23b-27de7a008c27'}, "hljs.highlightBlock(document.getElementById('612f6924-9d90-4036-a23b-27de7a008c27'))")))), m('p', '\nPretty easy!'), m('h3', 'FullImage'), m('p', 'This image is intended to center itself in the container and not exceed the maximum width. Here is an example:'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('img', {'style': {'max-width': '100%', 'display': 'block', 'margin': '0 auto'}, 'src': 'http://www.gnuplotting.org/figs/klein_bottle.png', 'alt': 'klein bottle'}), '\n'), m('div', {'style': {'flex': 1}}, m('pre', m('code#26ef3ebe-9cca-48d3-8ba5-b906166d61b7.language-md', '![klein bottle](http://www.gnuplotting.org/figs/klein_bottle.png)\n'), m('script', {'key': '26ef3ebe-9cca-48d3-8ba5-b906166d61b7'}, "hljs.highlightBlock(document.getElementById('26ef3ebe-9cca-48d3-8ba5-b906166d61b7'))")))), m('p', '\nHere it is rendered at full size\n', m('img', {'style': {'max-width': '100%', 'display': 'block', 'margin': '0 auto'}, 'src': 'http://www.gnuplotting.org/figs/klein_bottle.png', 'alt': 'klein bottle'})), m('p', 'And here is another image which is big enough to take up the whole container, and therefore will be constrained:'), m('p', m('img', {'style': {'max-width': '100%', 'display': 'block', 'margin': '0 auto'}, 'src': 'http://i.imgur.com/R1fJq0V.jpg', 'alt': 'bubble nebula'})), m('h2', 'Standalone Blocks'), m('p', 'The subtitle of this library is "plain text syntax for other plain text syntaxes". This is the section where I show you just how easy it is to use the other syntaxes out there with no special mangling or updating of a parser. Inside each of these environments, the text is processed by the respective library that is integrated, so you have access to anything that they\'ve defined.'), m('h3', 'Math!'), m('p', 'Math, math, math. For when nothing less than an equation will do. There are many math libraries out in the cyberwebs, but I chose ', m('a', {'href': 'https://khan.github.io/KaTeX/'}, 'KaTeX'), ' because its the most performant one out of all of them.'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('div.katex', m('div#katex-1a5b016d-721c-4f0a-ad0f-a7c812888c16'), m('script', {'key': 'katex-1a5b016d-721c-4f0a-ad0f-a7c812888c16'}, "katex.render('\\\\displaystyle{f(x) = \\\\int_{-\\\\infty}^\\\\infty\\n    \\\\hat f(\\\\xi)\\\\,e^{2 \\\\pi i \\\\xi x}\\n    \\\\,d\\\\xi}', document.getElementById('katex-1a5b016d-721c-4f0a-ad0f-a7c812888c16'))"))), m('div', {'style': {'flex': 1}}, m('pre', m('code#6c471a9c-b6bb-4b41-a9b3-b5a531480a2a.language-md', '---katex\nf(x) = \\int_{-\\infty}^\\infty\n    \\hat f(\\xi)\\,e^{2 \\pi i \\xi x}\n    \\,d\\xi\n...\n'), m('script', {'key': '6c471a9c-b6bb-4b41-a9b3-b5a531480a2a'}, "hljs.highlightBlock(document.getElementById('6c471a9c-b6bb-4b41-a9b3-b5a531480a2a'))")))), m('h3', 'Code Blocks'), m('p', 'Programming snippets are a common thing to include on technical websites. Again, there are many choices for syntax highlighting, and I have integrated ', m('a', {'href': 'https://highlightjs.org'}, 'highlight.js'), ' for now. See "Anatomy of a Component" to write a component to use a different one, like ', m('a', {'href': 'https://github.com/google/code-prettify'}, 'Google Prettify'), ' or ', m('a', {'href': 'https://craig.is/making/rainbows'}, 'rainbow.js'), '.'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('pre', m('code#1a179831-072b-4fca-bf89-967f3cbb7540.language-python', 'import toolz as t\n\ndef f(x):\n  return t.pipe(x,\n                t.map(lambda x: x+1))\n'), m('script', {'key': '1a179831-072b-4fca-bf89-967f3cbb7540'}, "hljs.highlightBlock(document.getElementById('1a179831-072b-4fca-bf89-967f3cbb7540'))"))), m('div', {'style': {'flex': 1}}, m('pre', m('code#79d57793-698e-40eb-9953-e285b7e10679.language-md', '---code python\nimport toolz as t\n\ndef f(x):\n  return t.pipe(x,\n                t.map(lambda x: x+1))\n...\n'), m('script', {'key': '79d57793-698e-40eb-9953-e285b7e10679'}, "hljs.highlightBlock(document.getElementById('79d57793-698e-40eb-9953-e285b7e10679'))")))), m('p'), m('h3', 'Annotated Code Blocks'), m('p', 'It can be a nice way to show off a code example so that the flow of the code is unbroken, but there are appropriate comments on the side.'), m('p', 'The default language for the code block is ', m('code', {}, 'python'), ', but you can change it to whatever you like. In order for the annotations to work properly, you will also have to include the character(s) that start a comment line as another argument:'), m.component(AnnotatedCode, {'language': 'haskell', 'annotations': {0: 'Type annotation (optional)\n', 2: 'Using recursion\n', 5: 'Using recursion, with guards\n', 9: 'Using recursion but written without pattern matching\n', 11: 'Using a list\n', 13: 'Using fold (implements product)\n', 15: 'Point-free style\n'}, 'code': 'factorial :: (Integral a) => a -> a\n\nfactorial n | n < 2 = 1\nfactorial n = n * factorial (n - 1)\n\nfactorial n\n  | n < 2     = 1\n  | otherwise = n * factorial (n - 1)\n\nfactorial n = if n > 0 then n * factorial (n-1) else 1\n\nfactorial n = product [1..n]\n\nfactorial n = foldl (*) 1 [1..n]\n\nfactorial = foldr (*) 1 . enumFromTo 1'}), m('p', '\nIn ', m('code', {}, 'Haskell'), ', comments begin with a ', m('code', {}, '--'), ' rather than a ', m('code', {}, '#'), ', so I passed that as the second argument. The code required to make the block above looks like this:'), m('pre', m('code#02e44f20-359e-4b00-ab1c-8cd26c38e2f0.language-python', '---annotated-code haskell --\n-- Type annotation (optional)\nfactorial :: (Integral a) => a -> a\n\n-- Using recursion\nfactorial n | n < 2 = 1\nfactorial n = n * factorial (n - 1)\n\n-- Using recursion, with guards\nfactorial n\n  | n < 2     = 1\n  | otherwise = n * factorial (n - 1)\n\n-- Using recursion but written without pattern matching\nfactorial n = if n > 0 then n * factorial (n-1) else 1\n\n-- Using a list\nfactorial n = product [1..n]\n\n-- Using fold (implements product)\nfactorial n = foldl (*) 1 [1..n]\n\n-- Point-free style\nfactorial = foldr (*) 1 . enumFromTo 1\n...\n'), m('script', {'key': '02e44f20-359e-4b00-ab1c-8cd26c38e2f0'}, "hljs.highlightBlock(document.getElementById('02e44f20-359e-4b00-ab1c-8cd26c38e2f0'))")), m('h3', 'Sheet Music (musicalabc)'), m('p', m('a', {'href': 'http://abcnotation.com/examples'}, 'musicalabc'), ' is a simple sheet music syntax, for which there is a js implementation of the parser.'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('div.musical-abc', m('div#musical-abc-1e17ff1d-8925-49f4-916f-f36ce99cd21a'), m('script', {'key': 'musical-abc-1e17ff1d-8925-49f4-916f-f36ce99cd21a'}, "ABCJS.renderAbc(document.getElementById('musical-abc-1e17ff1d-8925-49f4-916f-f36ce99cd21a'), 'X:1\\nT: Name\\nL: 1/2\\nC D E F| G A B C |\\n'); setViewBox('musical-abc-1e17ff1d-8925-49f4-916f-f36ce99cd21a');"))), m('div', {'style': {'flex': 1}}, m('pre', m('code#5d369ac0-0c9b-41a3-af22-785d4a2d8363.language-md', '---musical-abc\nX:1\nT: Name\nL: 1/2\nC D E F| G A B C |\n...\n'), m('script', {'key': '5d369ac0-0c9b-41a3-af22-785d4a2d8363'}, "hljs.highlightBlock(document.getElementById('5d369ac0-0c9b-41a3-af22-785d4a2d8363'))")))), m('p', '\nVoila! Pretty cool huh?'), m('h3', 'Guitar Chords'), m('p', 'Continuing in the music theme, someone wrote a JS function to draw guitar chord diagrams.'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('div.guitar-chord', m('svg#guitar-chord-75cc74d1-5940-406c-88ca-a3840ed2de10'), m('script', {'key': 'guitar-chord-75cc74d1-5940-406c-88ca-a3840ed2de10'}, "chordMaker()(document.getElementById('guitar-chord-75cc74d1-5940-406c-88ca-a3840ed2de10'), {'title': 'E Major', 'fret': '0, 2, 2, 1, 0, 0', 'label': '0, 2, 3, 1, 0, 0'})"))), m('div', {'style': {'flex': 1}}, m('pre', m('code#bcdac4ac-aa0f-4bf0-ba63-21b4e987b2f9.language-md', '---guitar-chord\ntitle: E Major\nfret: 0, 2, 2, 1, 0, 0\nlabel: 0, 2, 3, 1, 0, 0\n...\n'), m('script', {'key': 'bcdac4ac-aa0f-4bf0-ba63-21b4e987b2f9'}, "hljs.highlightBlock(document.getElementById('bcdac4ac-aa0f-4bf0-ba63-21b4e987b2f9'))")))), m('p', '\nEasy and cool! ', m('code', {}, 'fret'), ' controlls the position of the black dots (', m('code', {}, '0'), ' for open string), and ', m('code', {}, 'label'), ' is for the fingering on each of the 6 strings. You can also do ukelele, or any other differently stringed instrument, by just including more or less entries:'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m('div.guitar-chord', m('svg#guitar-chord-d349fc88-8c8e-4bd0-be91-910116df2e93'), m('script', {'key': 'guitar-chord-d349fc88-8c8e-4bd0-be91-910116df2e93'}, "chordMaker()(document.getElementById('guitar-chord-d349fc88-8c8e-4bd0-be91-910116df2e93'), {'title': 'E Major', 'fret': '0, 2, 2, 1', 'label': '0, 2, 3, 1'})"))), m('div', {'style': {'flex': 1}}, m('pre', m('code#8385b8b6-7e9d-464a-a553-16bfde00e9c1.language-md', '---guitar-chord\ntitle: E Major\nfret: 0, 2, 2, 1\nlabel: 0, 2, 3, 1\n...\n'), m('script', {'key': '8385b8b6-7e9d-464a-a553-16bfde00e9c1'}, "hljs.highlightBlock(document.getElementById('8385b8b6-7e9d-464a-a553-16bfde00e9c1'))")))), m('p', '\nHere is E Major for a tenor ukelele (which has the same tuning as the first four strings of a guitar).'), m('h2', 'Custom Components'), m('p', 'For those who like using a component library like React, Mithril, etc. You will probably write your own components a lot. It can be annoying to have to write something corresponding in ', m('strong', {}, 'GLUE'), ' for every single component you write in React or Mithril. There is an easy way around this though - there is a ', m('strong', {}, 'GLUE'), ' environment that allows you to use your own components, ', m('code', {}, 'YamlComponent'), ':'), m('div', {'style': {'display': 'flex', 'align-items': 'center'}}, m('div', {'style': {'flex': 1}}, m.component(AnnotatedCode, {'language': 'python', 'annotations': {0: 'annotation'}, 'code': 'blah blah blah'})), m('div', {'style': {'flex': 1}}, m('pre', m('code#2aa727c6-e256-48f4-b906-9a00df7c2495.language-md', '---yaml-component AnnotatedCode\ncode: blah blah blah\nlanguage: python\nannotations:\n  0: annotation\n...\n'), m('script', {'key': '2aa727c6-e256-48f4-b906-9a00df7c2495'}, "hljs.highlightBlock(document.getElementById('2aa727c6-e256-48f4-b906-9a00df7c2495'))")))), m('p', "\nHere I've put an ", m('code', {}, 'AnnotatedCode'), ' component (written in mithril.js) into my document by giving ', m('code', {}, 'YamlComponent'), ' the name of the component in the environment opening line (', m('code', {}, '---yaml-component AnnotatedCode'), ') and then filling in whatever information needs to be the ', m('code', {}, 'props'), ' (from React terminology, it may be called different things in different libraries) in YAML syntax in the body of the environment.'), m('h2', 'Wrap Up'), m('p', "That's a wrap! All the components that come with the Standard library. Hopefully this gives you an idea of the scope of the project and what it can accomplish. Most of these environments are also really easy to write, but that's the subject of another post."));
    }
  };
  
