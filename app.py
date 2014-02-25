# from http://docs.python.org/2/library/wsgiref.html
import jinja2
from wsgiref.util import setup_testing_defaults
import cgi
from urlparse import parse_qs

# A relatively simple WSGI application. 
class webApp:
    def __init__(self):
        # declare these now, set them later
        # send at end of run
        self.status = ''
        self.headers = []
        self.output = []
        loader = jinja2.FileSystemLoader('./templates')
        self.env = jinja2.Environment(loader=loader)

    def run(self, environ, start_response):
        self.status = ''
        self.headers = []
        self.output = []
        self.environ = environ

        self.path = self.environ['PATH_INFO']

        if environ['REQUEST_METHOD'] == 'GET':
            self.handle_GET()
        elif environ['REQUEST_METHOD'] == 'POST':
            self.handle_POST()

        # status, headers, and output should be set by now
        # so we can go ahead and send it all back to the server
        start_response(self.status, self.headers)
        return self.output

    def handle_GET(self):
        if self.path == '/':
            self.render('index.html')
        elif self.path == '/file':
            self.serve_txt_file()
        elif self.path == '/image':
            self.server_jpeg()
        else:
            filename = '%s.html' % (self.path.strip('/'))
            if filename == 'submit.html':
                query_string = self.environ['QUERY_STRING']
                query = parse_qs(query_string)
                self.handle_form(query)
            else:
                self.render(filename)

    def handle_POST(self):
        # check if empty to avoid IndexError
        if self.environ['CONTENT_TYPE']:
            content_type = self.environ['CONTENT_TYPE'].split()[0]
        else:
            content_type = ''
        # set the fields needed by cgi
        cgi_headers = {}
        
        # break here?
        cgi_headers['content-length'] = self.environ['CONTENT_LENGTH']
        cgi_headers['content-type'] = self.environ['CONTENT_TYPE']
        cgi_env = {}
        cgi_env['REQUEST_METHOD'] = 'POST'

        form = cgi.FieldStorage(headers=cgi_headers,
                                fp=self.environ['wsgi.input'],
                                environ=cgi_env)

        # build a query dict of the form input to send to handle_form
        query = {}
        try:
            query['firstname'] = form['firstname'].value
        except (KeyError, TypeError):
            query['firstname'] = ''
        try:
            query['lastname'] = form['lastname'].value
        except (KeyError, TypeError):
            query['lastname'] = ''

        # Handle either POST form
        if content_type == 'multipart/form-data;':
            if self.path == '/submit':
                self.handle_form(query)
            else:
                self.render('hello_post.html')
        elif content_type == 'application/x-www-form-urlencoded':
            if self.path == '/submit':
                self.handle_form(query)
            else:
                self.render('hello_post.html')
        else:
            self.render('enc_not_found.html',)

    def handle_form(self, query):
        try:
            f_name = ''.join(query['firstname'])
        except KeyError:
            f_name = ''
        try:
            l_name = ''.join(query['lastname'])
        except KeyError:
            l_name = ''
        vars = dict(firstname=f_name, lastname=l_name)
        self.render('submit.html', vars)

    def serve_txt_file(self):
        self.status = '200 OK'
        self.headers = [('Content-type', 'text/plain')]
        filename = 'textfile.txt'
        fp = open(filename, "rb")
        data = fp.read()
        fp.close()
        self.output = [data]

    def server_jpeg(self):
        self.status = '200 OK'
        self.headers = [('Content-type', 'image/jpeg')]
        filename = 'dog.jpg'
        fp = open(filename, "rb")
        data = fp.read()
        fp.close()
        self.output = [data]

    # parameters: filename: file to render,
    # vars: optional dictionary to html
    def render(self, filename, vars={}):
        self.headers = [('Content-type', 'text/html')]
        # encode makes it into a string
        try:
            template = self.env.get_template(filename).render(vars).encode('latin-1', 'replace')
            self.status = '200 OK'
        except jinja2.exceptions.TemplateNotFound:
            template = self.env.get_template('404.html').render().encode('latin-1', 'replace')
            self.status = '404 Not Found'
        self.output = [template]

def make_app():
    app = webApp()
    return app.run


