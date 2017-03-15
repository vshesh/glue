(function() {

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

var debouncedRenderText = _.debounce(renderText, 100);

var BlockEditor = {
  controller: function() {
    return {
      text: m.prop(null),
      template: m.prop(['div']),
      editing: m.prop(false)
    }
  },
  view: function(vm, props) {
    return m('div.block-editor',
      vm.editing() ? m('div#input', {style: 'height: 200px; position: relative;'},
        m('textarea', {value: vm.text(), oninput: function(e) {
          vm.text(e.target.value);
          debouncedRenderText(e.target.value).then(vm.template);
        }}),
        m('button', {style: 'position: absolute; top: 0; right: 0;',
                     onclick: e => vm.editing(false)}, 'done')
      ) : m('button', {style: 'flex: none; width: 50px; margin-left: calc(100% - 50px);',
                      onclick: e => vm.editing(true)}, 'Edit'),
      m('div#rendered', {style: 'flex: 1; overflow-y: scroll;'},
        makeElem(vm.template())));
  }
};

range = (n) => Array.apply(null, Array(n)).map((_, i) => i)

var List = (comp) => {
  controller: function() {
    return {
      children: m.prop([])
    }
  },
  view: function(vm) {
    return m('div', vm.children().map((e,i) =>
      m('div', {key: i},
        m.component(comp),
        m('button', {onclick: e => vm.children(vm.children.splice(i,1))}, 'Remove'))
    ))
  }
}

var Editor = {
  controller: function() {
    return {
      numblocks: m.prop(0)
    }
  },
  view: function(vm) {
    vm.blocks().map((b,i) => m.component(BlockEditor, b))
  }
}

m.mount(document.getElementById('container'), m.component(BlockEditor));

})();
