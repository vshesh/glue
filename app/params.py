# File: params.py
# Author: Vishesh Gupta
# Created: June 2015

from bottle import request, response, abort, error, HTTPResponse

import simplejson as json
import toolz as t
import sys


def typename(o):
  """Returns classname of `o` in single quotes.
  eg, typename([]) -> '\\'list\\''"""
  return str(type(o))[7:-1]


def reqinfo():
  """Gives path + method + JSON body of request

  This is the minimum information to figure out what went wrong with the
  request that was made to the server.
  """
  return {'path':request.path,
          'method' : request.method,
          'params': json.dumps({k:request.params[k] for k in request.params}
                               if request.json == None else request.json,
                               iterable_as_array=True)}


def jsonabort(status,message):
  """Usage: jsonabort(400, 'message') - works just like abort, but json.

  For JSON REST API, need to be able to send consistent error message with
  a cause statement and a status code, along with some information about the
  request that was made to cause the error.

  this is a parallel function to abort (provided by bottle.py) so use
  accordingly. however, it raises HTTPResponse, and so will NOT be
  caught by other handlers - it's just a clean exit.
  """
  if type(status) is not int:
    abort(500, 'jsonabort requires integer status, got {}'.format(
            typename(status)))
  if type(message) is not str:
    abort(500, 'jsonabort requires string message, got {}'.format(
            typename(message)))

  raise HTTPResponse(status=status, headers={'Content-Type':'application/json'},
                     # TODO(vishesh): should return the entire request object?
                     body=json.dumps({'message':message, 'request':reqinfo()}))


def params(keys=[], opts={}, strict=True):
  """Decorator: Basic request verification for json REST endpoints

  Checks that the request is valid json, that the json returned is an
  object (since lists can lead to XSS attacks and are discouraged in
  json apis) and that all the keys in `keys` are present in the request.

  In strict mode, the request is not allowed to have extraneous keys
  that aren't present in `keys` or `opts`.

  Most requests will want to be strict, I can't imagine why you would
  want a non-key (required field), non-opt (optional field) parameter
  in the request you're making. What other kinds of fields are there?
  However, leaving the option here for the time being - it might be useful
  to relax the requirement while developing and the keys aren't finalized.

  This function will pass through the named keys and opts through to the
  wrapped function BY NAME.
  If you say `@params(['x'])`, you will have to define a parameter named
  `x` in your function:

  ```python
  @params(['x'])
  def take_x(x):
    pass
  ```

  The keys/opts are passed as keyword-args, so they can occur in any order
  in your function signature.
  Note that the params passed through the JSON request will CLOBBER
  kwargs the function is called with.
  So if you have a route param, don't have an expected JSON param of the same
  name (again, why on earth would you want this)

  This is BAD:

  ```python
  @route('/test/<x>')
  @params(['x'])
  def f(x):
    pass
  ```

  You will never see the x value from the route.
  This function will throw an error if there's an overlap, so that you can't
  do that by accident.
  """
  def reqjson(req_fun):
    # pass through all args to req_fun
    def requirejson_wrapper(*args, **kwargs):

      # TODO(vishesh): malformed JSON gives 500 error, should give 400,
      # can't seem to catch the ValueError from json.loads
      try:
        # GET/DELETE have no body. PUT/PATCH/POST have bodies.
        r = None
        if (request.method in ['GET', 'DELETE'] or
           (request.method in ['POST', 'PUT', 'PATCH'] and
            'json' not in request.content_type)):
            r = {k: request.params[k] for k in request.params}
        else:
            r = request.json
      except ValueError as e:
        jsonabort(400, ('Request should be parseable json, got error: '
                        ''+str(e.args)))

      if r == None:
        # the only time that r will be None is if the json part fails.
        # request.params being empty will give an empty dictionary instead,
        # so this logic is okay (don't need to change the expected
        # content-type based on the request method).
        jsonabort(400, ('Content-Type should be application/json, got '
                        ''+str(request.content_type)))

      if type(r) is not dict:
        jsonabort(400, 'Request must be a JSON object, not {}'.format(
            typename(r)))

      if not all(k in r for k in keys):
        jsonabort(400, 'Request is missing keys: ' +
                  str(list(set(keys) - r.keys())))

      if strict and not all(p in keys or p in opts for p in r):
        # since we know that all k in keys is present in r
        # if the lengths are unequal then for sure there are extra keys.
        jsonabort(400, 'Strict mode: request has unrecognized keys: ' +
                  str(list(r.keys() - set(keys))))
      

      p = t.keymap(lambda k: k.replace('-', '_'), t.merge(opts, r))

      # python 3.5+ type checking, replace known types with variables.
      if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
        ann = req_fun.__annotations__
        for (k,v) in p.items():
          if k in ann:
            try:
              p[k] = ann[k](v)
            except:
              jsonabort(400,
                'Parameter {} should be type {}, got {}'.format(
                  k, ann[k], type(v)))

      overlap = set(kwargs) & set(p)
      if len(overlap) > 0:
        raise ValueError(
          'keyword args being clobbered by json params: ' + str(overlap))

      return req_fun(*args, **t.merge(kwargs, p))

    return requirejson_wrapper
  return reqjson
