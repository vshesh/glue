(function() {

var Katex = {
  controller: function() {},
  view: function(vm, args) {
    return ['div.math', {config: function(element) {
      katex.render(args.text, element);
    }}]
  }
}

var componentMap = {
  'Katex': Katex
}

function makeElem(html) {
  if (_.isArray(html)) {
    if (_.isArray(html[0])) {
      return _.map(html, makeElem);
    }
    if (/^[A-Z][a-zA-Z0-9_]*$/.test(html[0])) {
      return _.concat([m.component(eval(html[0]), html[1])], _.map(html.slice(2), makeElem));
    }
    return _.partial(m, html[0]).apply(null, _.map(html.slice(1), makeElem));
  } else {
    return html;
  }
}

function renderText(text) {
  return m.request({url: '/render',
             method: 'POST',
             data: {'text': text},
             unwrapSuccess: x => x.template})
}

var debouncedRenderText = _.debounce(renderText, 100, {maxWait: 100});


var Root = {
  controller: function() {
    return {
      text: m.prop('# Placeholder'),
      template: m.prop(['div', ['h1', 'Placeholder']])
    }
  },
  view: function(vm) {
    return m('div', {style: 'display: flex;'},
      m('div#input', {style: 'flex: 1;'},
        m('textarea', {value: vm.text(), oninput: function(e) {
          vm.text(e.target.value);
          debouncedRenderText(e.target.value).then(vm.template);
        }})
      ),
      m('div#rendered', {style: 'flex: 1; overflow-y: scroll;'},
        makeElem(vm.template())));
  }
};

m.mount(document.getElementById('container'), m.component(Root));

})();
