# image handling API
import sqlite3
IMAGE_DB_FILE='images.sqlite'

import os

images = {}

def initialize():
    load()

def load():
    global images
    if not os.path.exists(IMAGE_DB_FILE):
        print 'CREATING', IMAGE_DB_FILE
        db = sqlite3.connect(IMAGE_DB_FILE)
        db.execute('CREATE TABLE image_store (i INTEGER PRIMARY KEY, image BLOB)');
        db.commit()
        db.close()

    # connect to database
    db = sqlite3.connect(IMAGE_DB_FILE)

    # configure to retrieve bytes, not text
    db.text_factory = bytes

    # get a query handle (or "cursor")
    c = db.cursor()

    # select all of the images
    c.execute('SELECT i, image FROM image_store')
    for i, image in c.fetchall():
        images[i] = image
    
def add_image(data):
    if images:
        image_num = max(images.keys()) + 1
    else:
        image_num = 0
        
    # connect to the already existing database
    db = sqlite3.connect(IMAGE_DB_FILE)

    # configure to allow binary insertions
    db.text_factory = bytes

    # insert!
    db.execute('INSERT INTO image_store (i, image) VALUES (?, ?)',
               (image_num, data,))
    db.commit()

    images[image_num] = data
    
    return image_num

def get_image(num):
    return images[num]

def get_latest_image():
    image_num = max(images.keys())
    return images[image_num]
