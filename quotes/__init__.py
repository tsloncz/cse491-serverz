# __init__.py is the top level file in a Python package.

from quixote.publish import Publisher
import sys

# this imports the class RootDirectory from the file 'root.py'

from apps import QuotesApp


 
def setup(): # stuff that should be run once.
    quotes_app = QuotesApp('quotes/quotes.txt', './html')
    return quotes_app


    

def teardown(): # stuff that should be run once.
    pass
