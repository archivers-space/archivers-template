# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

#TODO:
import scraperwiki
import requests
import json
from datetime import datetime
import hashlib

def initialize(url,UUID):
    """
    Should be called at the beginning of every scrape run (TODO: perhaps turn this into a decorator pattern)
    Creates the table for the runs metadata, and stores a timestamp, the http response headers, response body, and a SHA-256 hash of the body
    """
    makeTables()
    currentTime = str(datetime.now())
    r = requests.get(url)
    headers = json.dumps(dict(r.headers)) #json-serialized headers
    content = r.content #response body, TODO: may need to handle binary data differently vs html
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest() #SHA-256 hash of body - text is first encoded as utf-8 b/c sha256 expects binary; output is then converted back as a hexadecimal string representation for storage
    payload = {'url':url,\
            'UUID':UUID,\
            'timestamp':currentTime,\
            'body_content':content,\
            'body_SHA256':content_hash,\
            'headers':headers}
    scraperwiki.sqlite.save(unique_keys=[],data=payload,table_name='runs_metadata') #saves to sqlite
    current_run_id = scraperwiki.sqlite.execute("""
            SELECT seq FROM sqlite_sequence WHERE NAME="runs_metadata"
            """) #Gets the most recent run_id associated w/ the entry we just added
    return current_run_id

def makeTables():
    """
    Creates a table in the sqlite db for keeping track of runs
    """
    scraperwiki.sqlite.execute("""
                    CREATE TABLE IF NOT EXISTS runs_metadata (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    UUID TEXT,
                    timestamp TEXT,
                    body_content TEXT,
                    body_SHA256 TEXT,
                    headers TEXT
                    )""")
    scraperwiki.sqlite.execute("""
                    CREATE TABLE IF NOT EXISTS child_urls (
                    url TEXT UNIQUE NOT NULL,
                    timestamp TEXT
                    )""")

def addURL(url):
    """
    add a child URL to the database
    """
    currentTime = str(datetime.now())
    payload = {'url':url,\
            'timestamp':currentTime}
    scraperwiki.sqlite.save(unique_keys=[],data=payload,table_name='child_urls')

def scrape(url,UUID):
    """
    This is the function that users should modify: they should make sure to store the run_id along with their data. Data should be saved to the sqlite table "data".
    Data can be saved using scraperwiki module via:
    scraperwiki.sqlite.save(unique_keys,data=dictionary_of_data,table_name='data')
    or any other connection capable of writing to the local sqlite db named data.sqlite
    """
    run_id = initialize(url,UUID)
    addURL('http://example.org') #test add a child URL
    addURL('http://example.org') #adding again doesn't do anything because of UNIQUE
    addURL('http://archivers.space') #adding a different URL does add an entry though
    return

if __name__ == '__main__':
    url = 'http://example.org'
    UUID = '0000'
    scrape(url,UUID)
