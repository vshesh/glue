function makeElem(html) {
  if (_.isArray(html)) {
    return _.partial(m, html[0]).apply(null, _.map(html.slice(1), makeElem));
  } else {
    return html;
  }
}

var Root = {
  controller: function() {
    return {
      text: m.prop('Placeholder')
    }
  },
  view: function(vm, template) {
    return m('div', {style: 'display: flex;'},
      m('div', {style: 'flex: 1;'},
        m('textarea', {value: vm.text(), onchange: function(e) {vm.text(e.target.value)} })),
      m('div', {style: 'flex: 1;'},
        makeElem(['div', 'hello world'])));
  }
};

m.mount(document.getElementById('container'), m.component(Root));
