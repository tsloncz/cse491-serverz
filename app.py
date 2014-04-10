# from http://docs.python.org/2/library/wsgiref.html
import jinja2
import cgi
import StringIO
import Cookie

def render_template(env, filename, vars = {}):
    template = env.get_template(filename)
    return template.render(vars).encode('latin-1', 'replace')

def file_contents(filename):
    fp = open(filename, 'rb')
    data = fp.read()
    fp.close()
    return data

def app(environ, start_response):
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']
    query_string = environ['QUERY_STRING']

    # Set up jinja2
    loader = jinja2.FileSystemLoader('./templates')
    env = jinja2.Environment(loader=loader)

    allowed_urls = dict()
    allowed_urls['/'] = 'index.html'
    allowed_urls['/content'] = 'content.html'
    allowed_urls['/file'] = 'textfile.txt'
    allowed_urls['/form'] = 'form.html'
    allowed_urls['/submit'] = 'submit.html'
    allowed_urls['/image'] = 'tux.png'
    allowed_urls['/style.css'] = 'style.css'

    vars = dict()
    if path == '/submit':
        if method == 'GET':
            parsed_query = urlparse.parse_qs(query_string)
            vars['firstname'] = parsed_query['firstname'][0]
            vars['lastname'] = parsed_query['lastname'][0]
        elif method == 'POST':
            # Get content
            content_type = environ['CONTENT_TYPE']
            content_length = int(environ['CONTENT_LENGTH'])
            content = environ['wsgi.input'].read(content_length)

            # Content type: application/x-www-form-urlencoded
            if content_type == 'application/x-www-form-urlencoded':
                parsed_query = urlparse.parse_qs(content)
                vars['firstname'] = parsed_query['firstname'][0]
                vars['lastname'] = parsed_query['lastname'][0]

            # Content type: multipart/form-data
            elif content_type.startswith('multipart/form-data'):
                headers = {}
                for key, val in environ.iteritems():
                    headers[key.lower().replace('_', '-')] = val
                fs = cgi.FieldStorage(fp=StringIO.StringIO(content),
                         headers = headers, environ = environ)
                vars['firstname'] = fs['firstname'].value
                vars['lastname'] = fs['lastname'].value
    if path in allowed_urls:

        filename = allowed_urls[path]

        if filename.endswith('.html'):
            start_response('200 OK', [('Content-type', 'text/html')])
            ret = render_template(env, filename, vars)
        elif filename.endswith('.css'):
            start_response('200 OK', [('Content-type', 'text/css')])
            ret = file_contents(filename)
        elif filename.endswith('.txt'):
            start_response('200 OK', [('Content-type', 'text/plain')])
            ret = file_contents(filename)
        elif filename.endswith('.png'):
            start_response('200 OK', [('Content-type', 'image/png')])
            ret = file_contents(filename)
    else:
        start_response('200 OK', [('Content-type', 'text/html')])
        ret = render_template(env, 'not_found.html', vars)

    # Needs to be a single-entry list for wsgi compliance
    return [ret]

def make_app():
    return app
