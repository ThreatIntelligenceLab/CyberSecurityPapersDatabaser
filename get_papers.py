import sys
import os
import sqlite3
import hashlib
from urllib.parse import urlparse
from datetime import datetime
from googlesearch import search
import requests



def create_directory():
    if not os.path.exists('Papers'):
        os.makedirs('Papers')

def create_db():
    conn = sqlite3.connect('papers.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS downloaded (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            thepaper BLOB,
            datetime TEXT,
            md5checksum TEXT,
            domain TEXT,
            query TEXT
        )
    ''')
    conn.commit()
    conn.close()
 

def domain_from_url(url):
    return urlparse(url).netloc

def download_content(url):
    try:
        response = requests.get(url,timeout=15)
        if response.status_code == 200:
            return response.content
    except:
        return None

def insert_into_db(query, url, pdf_content, md5checksum):
    if pdf_content:
        conn = sqlite3.connect('papers.db')
        c = conn.cursor()
        # Check if the file already exists based on the md5checksum
        c.execute('SELECT * FROM downloaded WHERE md5checksum = ?', (md5checksum,))
        if not c.fetchone():  # If the file is not in the database, insert it
            domain = domain_from_url(url)
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute('''
                INSERT INTO downloaded (url, thepaper, datetime, md5checksum, domain, query)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, pdf_content, current_datetime, md5checksum, domain, query))
            conn.commit()
        conn.close()

def get_md5_checksum(pdf_content):
    hasher = hashlib.md5()
    hasher.update(pdf_content)
    return hasher.hexdigest()

def main(query):
    create_db()
    xquery = "filetype:pdf "
    for i, url in enumerate(search(xquery + query, stop=20)):
        pdf_content = download_content(url)
        if pdf_content:
            md5checksum = get_md5_checksum(pdf_content)
            insert_into_db(query, url, pdf_content, md5checksum)

if __name__ == "__main__":
    main(sys.argv[1])