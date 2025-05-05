from flask import Flask, request, redirect, jsonify
import sqlite3
import string
import random

app = Flask(__name__)
DB_NAME = 'urls.db'

# Initialize database
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY, short TEXT UNIQUE, long TEXT)''')
conn.commit()
conn.close()

# Helper function to generate short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.json.get('url')
    if not long_url:
        return jsonify({'error': 'URL is required'}), 400

    short_code = generate_short_code()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO urls (short, long) VALUES (?, ?)", (short_code, long_url))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Short code conflict'}), 500
    finally:
        conn.close()

    return jsonify({'short_url': request.host_url + short_code})

@app.route('/<short_code>')
def redirect_url(short_code):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT long FROM urls WHERE short = ?", (short_code,))
    row = c.fetchone()
    conn.close()
    if row:
        return redirect(row[0])
    return jsonify({'error': 'URL not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
