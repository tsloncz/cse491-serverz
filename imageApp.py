import urlparse
import jinja2
import cgi
import time
import StringIO
import Cookie
import sqlite3
from app import render_template, file_contents

def image_app(environ, start_response):
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']
    query_string = environ['QUERY_STRING']
    redirect = False

    # Set up jinja2
    loader = jinja2.FileSystemLoader('./templates')
    env = jinja2.Environment(loader=loader)

    vars = dict()
    if path == '/image_upload':
        # Get content
        content_type = environ['CONTENT_TYPE']
        content_length = int(environ['CONTENT_LENGTH'])
        content = environ['wsgi.input'].read(content_length)
        headers = {}
        for key, val in environ.iteritems():
            headers[key.lower().replace('_', '-')] = val
        fs = cgi.FieldStorage(fp=StringIO.StringIO(content),
                              headers = headers, environ = environ)
        filename = fs['file'].filename
        image_type = filename.split('.')[-1]

        if image_type in {'png', 'jpg', 'tiff', 'jpeg'}:

            # connect to the already existing database
            db = sqlite3.connect('images.sqlite')

            # configure to allow binary insertions
            db.text_factory = bytes

            # data to be inserted into database
            r = fs['file'].value
            f = fs['file'].filename
            d = fs['description'].value
            u = 1

            # insert
            db.execute('INSERT INTO image_store (image, name, description, user_id) VALUES (?, ?, ?, ?)', (r, f, d, u))
            db.commit()
        
            start_response('302 Moved Temporarily',
                       [('Content-type', 'text/plain'),
                        ('Location', '/')])
            redirect = True
    if path == '/':
        db = sqlite3.connect('images.sqlite')

        # configure to retrieve bytes, not text
        db.text_factory = bytes

        # get a query handle (or "cursor")
        c = db.cursor()

        # select all of the images
        c.execute('SELECT iid, name, description, user_id FROM image_store ORDER BY iid DESC LIMIT 1')
        iid, name, description, user_id = c.fetchone()

        vars['name'] = name
        vars['description'] = description
        vars['time'] = time.time()
        start_response('200 OK', [('Content-type', 'text/html')])
        ret = render_template(env, 'imageapp.html', vars)
    elif path.startswith('/latest_image'):
        db = sqlite3.connect('images.sqlite')

        # configure to retrieve bytes, not text
        db.text_factory = bytes

        # get a query handle (or "cursor")
        c = db.cursor()

        # select all of the images
        c.execute('SELECT iid FROM image_store ORDER BY iid DESC LIMIT 1')
        iid, = c.fetchone()
        start_response('302 Moved Temporarily',
                       [('Content-type', 'text/plain'),
                        ('Location', '/image_raw/' + str(iid))])

        redirect = True
        
    elif path.startswith('/image_raw/'):
        image_no = path.lstrip('/image_raw/')
        db = sqlite3.connect('images.sqlite')

        # configure to retrieve bytes, not text
        db.text_factory = bytes

        # get a query handle (or "cursor")
        c = db.cursor()

        # select image with iid=image_no
        c.execute('SELECT image, name FROM image_store WHERE iid=?', (image_no,))

        image, name = c.fetchone()

        start_response('200 OK', [('Content-type',
                       'image/' + name.split('.')[-1])])
        ret = image

    else:
        start_response('200 OK', [('Content-type', 'text/html')])
        ret = render_template(env, 'not_found.html', vars)
    
    # Needs to be a single-entry list for wsgi compliance
    if redirect:
        return ['']
    else:
        return [ret]

def make_image_app():
    return image_app
