String.prototype.hashCode = function() {
  var hash = 0, i, chr, len;
  if (this.length === 0) return hash;
  for (i = 0, len = this.length; i < len; i++) {
    chr   = this.charCodeAt(i);
    hash  = ((hash << 5) - hash) + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
};

var AnnotatedCode = {
  controller: function(props) {
    return {
      annotation: m.prop('')
    }
  },
  view: function(ctrl, props) {
    indexMap = Object.keys(props.annotations).map((i,e) => [i,e]).reduce(
      (acc,p) => {acc[p[0]] = p[1]; return acc;}, {});
    return (
      m('div.annotated-code',
        m('div.code-box',
         m('pre.hljs', {style: "overflow-x: visible; margin-bottom: 0, border-top-left-radius: 3px; border-bottom-left-radius: 3px; border-right: 1px dotted grey"},
         [...Array(props.code.split('\n').length).keys()].map((e) => {
           if (e in props.annotations) {
             return m('span.annotation',
                      {key: e, onmouseenter: ev => ctrl.annotation(props.annotations[e])},
                      indexMap[e] + '\n')
           } else {
             return '\n'
           }
         })),
         m('pre', m('code.python',
           {key: props.code.hashCode(),
            config: elem => hljs.highlightBlock(elem)},
           props.code))),
       ctrl.annotation().trim().length > 0 ? m('div.hljs', ctrl.annotation() ) : m('div') ));
  }
}
