#Made by Reza Rafati
#From ThreatIntelligenceLab.com
#Date: 23-07-2024
#Description: This project creates a FLASK website with a database. It then uses the Google Search to find and download papers. A cookie will be made for this by the Google function.
#Please feel free to adjust this or use this tool internally. If it really works for you, please do let me know or leave a backlink to 'threatintelligencelab.com'. 
#'Threat Intelligence Lab' is active on LinkedIn. Follow us: https://www.linkedin.com/company/threat-intelligence-lab

from flask import Flask, render_template, request, send_from_directory
import subprocess
import sqlite3
import os
from get_papers import create_directory, create_db
   
app = Flask(__name__)


create_db()
create_directory()
def get_top_downloads():
    conn = sqlite3.connect('papers.db')
    c = conn.cursor()
    c.execute('SELECT * FROM downloaded ORDER BY id DESC LIMIT 10')
    downloads = c.fetchall()
    conn.close()
    return downloads

@app.route('/all')
def all_papers():
    conn = sqlite3.connect('papers.db')
    c = conn.cursor()
    c.execute('SELECT * FROM downloaded ORDER BY id DESC LIMIT 100')
    downloads = c.fetchall()
    conn.close()
    return render_template('all.html', downloads=downloads)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    downloads = [] 
    search_query = request.args.get('search_query')
    if request.method == 'POST':
        query = request.form['query']
        subprocess.run(['python', 'get_papers.py', query])
    elif search_query:
        downloads = search_papers(search_query)
    else:
        downloads = get_top_downloads()
    total_papers = get_total_papers()
    top_domains = get_top_domains()
    return render_template('index.html', downloads=downloads, total_papers=total_papers, top_domains=top_domains, search_query=search_query or "")

def search_papers(search_query):
    conn = sqlite3.connect('papers.db')
    c = conn.cursor()
    search_term = f"%{search_query}%"
    c.execute('SELECT * FROM downloaded WHERE domain LIKE ? OR url LIKE ?', (search_term, search_term))
    results = c.fetchall()
    conn.close()
    return results


def get_total_papers():
    conn = sqlite3.connect('papers.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM downloaded')
    total = c.fetchone()[0]
    conn.close()
    return total

def get_top_domains():
    conn = sqlite3.connect('papers.db')
    c = conn.cursor()
    c.execute('''
        SELECT domain, COUNT(domain) AS count FROM downloaded
        GROUP BY domain ORDER BY count DESC LIMIT 10
    ''')
    top_domains = c.fetchall()
    conn.close()
    return top_domains


from flask import send_file, Response

@app.route('/download/<int:download_id>')
def download_file(download_id):
    conn = sqlite3.connect('papers.db')
    c = conn.cursor()
    c.execute('SELECT thepaper, domain FROM downloaded WHERE id = ?', (download_id,))
    paper = c.fetchone()
    conn.close()
    if paper:
        return Response(
            paper[0],
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment;filename=" + paper[1] + ".pdf"}
        )
    return 'File not found', 404


if __name__ == '__main__':
    app.run(debug=True)
