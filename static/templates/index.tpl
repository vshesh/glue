<!DOCTYPE html>
<html>
<head>
  {{!assets}}
  <script src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.13.1/lodash.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/mithril/0.2.5/mithril.min.js"></script>
  <link href="https://fonts.googleapis.com/css?family=Ribeye+Marrow" rel="stylesheet">
  <link rel="stylesheet" href="/css/app.css">
</head>
<body>
  <div id="container"></div>
  <script src="/js/elm.js"></script>
  <script>
    Elm.Main.embed(document.getElementById('container'))
  </script>
</body>
</html>
