import sqlite3

db = sqlite3.connect('images.sqlite')
db.execute('CREATE TABLE image_store (iid INTEGER PRIMARY KEY AUTOINCREMENT, image BLOB, name VARCHAR(20), description VARCHAR(200), user_id INTEGER)')
db.execute('CREATE TABLE users (uid INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(20), password VARCHAR(20))')
db.commit()
db.close()
