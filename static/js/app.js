function makeElem(html) {
  if (_.isArray(html)) {
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

var debouncedRenderText = _.throttle(renderText, 100);

var Root = {
  controller: function() {
    return {
      text: m.prop('# Placeholder'),
      template: m.prop(['div', ['h1', 'Placeholder']])
    }
  },
  view: function(vm, template) {
    return m('div', {style: 'display: flex;'},
      m('div', {style: 'flex: 1;'},
        m('textarea', {value: vm.text(), oninput: function(e) {
          vm.text(e.target.value);
          debouncedRenderText(e.target.value).then(vm.template);
        }})
      ),
      m('div', {style: 'flex: 1;'},
        makeElem(vm.template())));
  }
};

m.mount(document.getElementById('container'), m.component(Root));
