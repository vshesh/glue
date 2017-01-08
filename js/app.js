function loadJS(file) {
  // DOM: Create the script element
  var jsElm = document.createElement("script");
  // set the type attribute
  jsElm.type = "application/javascript";
  // make the script element load file
  jsElm.src = file;
  // finally insert the element to the body element in order to load the script
  document.body.appendChild(jsElm);
  // return jsElm to add events, if desired:
  return jsElm;
}

loadJS('/js/anatomy.js').onload = function() {
  loadJS('/js/intro.js').onload = function() {
    loadJS('/js/markdown.js').onload = function() {
      loadJS('/js/tour.js').onload = function() {
        m.route(document.getElementById('container'), '/', {
          '/': Intro,
          '/intro': Intro,
          '/tour': Tour,
          '/markdown': Markdown,
          '/anatomy': Anatomy
        })
      }
    }
  }
}