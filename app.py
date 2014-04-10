# from http://docs.python.org/2/library/wsgiref.html
import jinja2
import re

from cgi import parse_qs, escape, FieldStorage

def base_app(environ, start_response):
    return app(environ,start_response)

def make_app():
    return base_app

def handle_submit(environ, start_response, jinja):
    start_response('200 OK', [('Content-Type', 'text/html')])
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
    return jinja.get_template("submit.html").render(params)

def handle_form(environ, start_response, jinja):
    start_response('200 OK', [('Content-Type', 'text/html')])
    params = {'title':'Super Cool Form Page'}
    return jinja.get_template('form.html').render(params)

def handle_root(environ, start_response, jinja):
    start_response('200 OK', [('Content-Type', 'text/html')])
    params = {'title':'Welcome to Zombo.com (this is not Zombo.com)'}
    return jinja.get_template('index.html').render(params)

def handle_content(environ, start_response, jinja):
    start_response('200 OK', [('Content-Type', 'text/html')])
    params = {'title':'Content-ish'}
    return jinja.get_template('content.html').render(params)

def handle_file(environ, start_response, jinja):
    fp = open("textfile.txt","rb")
    data = fp.read()
    fp.close
    env = {}
    env= [('Content-Length', str(len(data))),('Content-Type', 'text/plain')]
    start_response('200 OK', env)

    return data;

def handle_image(environ, start_response, jinja):
    fp = open("dog.jpg","rb")
    data = fp.read()
    fp.close
    env = {}
    env= [('Content-Length', str(len(data))),('Content-Type', 'image/jpeg')]
    start_response('200 OK', env)

    return data;

def handle_404(environ, start_response, jinja):
    start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
    params = {'title':'Son, are you lost!?'}
    return jinja.get_template("404.html").render(params)

    
def app(environ,start_response):
    loader = jinja2.FileSystemLoader('./templates')
    jinja = jinja2.Environment(loader=loader)

    encodeFlag = True;

    path = environ.get('PATH_INFO', '')
    if path == '/':
        content = handle_root(environ, start_response, jinja)
    elif path == '/content':
        content = handle_content(environ, start_response, jinja)
    elif path == '/image':
        content = handle_image(environ, start_response, jinja)
        encodeFlag = False;
    elif path == '/file':
        content = handle_file(environ, start_response, jinja)
        encodeFlag = False;
    elif path == '/form':
        content = handle_form(environ, start_response, jinja)
    elif "/submit" in path:
        content = handle_submit(environ, start_response, jinja)
    else:
        content = handle_404(environ, start_response, jinja)
    # flatten content form unicode to a string
    if encodeFlag:
        content = content.encode('latin-1', 'replace')

    return [content]


