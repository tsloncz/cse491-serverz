# from http://docs.python.org/2/library/wsgiref.html
import jinja2
from wsgiref.util import setup_testing_defaults
import cgi
from urlparse import parse_qs

# A relatively simple WSGI application. It's going to print out the
# environment dictionary after being updated by setup_testing_defaults
def simple_app(environ, start_response):
    loader = jinja2.FileSystemLoader('./templates')
    env = jinja2.Environment(loader=loader)
    
    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)
    
    path =  environ['PATH_INFO']
    print 'path: ',path
    if path == '/':
            ret = handle_root(environ, start_response, env)
    elif path == '/form':
            ret = handle_form(environ, start_response, env)
    elif path == '/file':
            ret = handle_file(environ, start_response, env)
    elif path == '/content':
            ret = handle_content(environ, start_response, env)
    elif path == '/image':
            ret = handle_image(environ, start_response, env)
    elif path == '/submit':
            ret = handle_submit(environ, start_response, env)
    else:
            ret = handle_404(environ, start_response, env)
    return ret

def make_app():
    return simple_app


def handle_submit(environ, start_response, env):
          path = environ.get('PATH_INFO', '')
          method = environ.get('REQUEST_METHOD','')
          content_type = environ.get('CONTENT_TYPE', '')
          if method == "POST":
              stream = environ.get('wsgi.input','')
              form = FieldStorage(fp=stream, environ=environ)
              params = {}
              params['firstname'] = form['firstname'].value
              params['lastname'] = form['lastname'].value
          elif method == "GET":
              query = parse_qs(environ.get('QUERY_STRING',''))
              params = {}
              params['firstname'] = query['firstname'][0]
              params['lastname'] = query['lastname'][0]
          params['title'] = "Results"
          return env.get_template("submit.html").render(params)

def handle_form(environ, start_response, env):
      params = {'title':' Form Page'}
      return env.get_template('form.html').render(params)

def handle_root(environ,start_response, env):
      params = {'title':'Home'}
      return env.get_template('index.html').render(params)

def handle_content(environ, start_response, env):
      params = {'title':'Content Page'}
      return env.get_template('image.html').render(params)

def handle_file(environ,start_response, env):
      params = {'title':'Files Page'}
      return env.get_template('file.html').render(params)

def handle_image(environ,start_response, env):
      params = {'title':'Image Page'}
      return env.get_template('image.html').render(params)

def handle_404(environ, start_response, env):
      params = {'title':'Son, are you lost!?'}
      return env.get_template("404.html").render(params)
