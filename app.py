from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'library_secret_key'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route
@app.route('/')
def home():
    return redirect('/login')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['user'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html')
    return redirect('/login')

# Add book
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user' in session:
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            year = request.form['year']
            conn = get_db_connection()
            conn.execute('INSERT INTO books (title, author, year) VALUES (?, ?, ?)',
                         (title, author, year))
            conn.commit()
            conn.close()
            return redirect('/view_books')
        return render_template('add_book.html')
    return redirect('/login')

# View books
@app.route('/view_books')
def view_books():
    if 'user' in session:
        conn = get_db_connection()
        books = conn.execute('SELECT * FROM books').fetchall()
        conn.close()
        return render_template('view_books.html', books=books)
    return redirect('/login')

# Delete book
@app.route('/delete_book/<int:id>')
def delete_book(id):
    if 'user' in session:
        conn = get_db_connection()
        conn.execute('DELETE FROM books WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return redirect('/view_books')
    return redirect('/login')

# Issue book
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    if 'user' in session:
        conn = get_db_connection()
        if request.method == 'POST':
            book_id = request.form['book_id']
            issued_to = request.form['issued_to']
            conn.execute('INSERT INTO issued (book_id, issued_to) VALUES (?, ?)',
                         (book_id, issued_to))
            conn.commit()
            conn.close()
            return redirect('/issued_books')
        books = conn.execute('SELECT * FROM books').fetchall()
        conn.close()
        return render_template('issue_book.html', books=books)
    return redirect('/login')

# Issued books list
@app.route('/issued_books')
def issued_books():
    if 'user' in session:
        conn = get_db_connection()
        issued = conn.execute('''
            SELECT i.id, b.title, i.issued_to
            FROM issued i
            JOIN books b ON b.id = i.book_id
        ''').fetchall()
        conn.close()
        return render_template('issued_books.html', issued=issued)
    return redirect('/login')

# Return book
@app.route('/return_book/<int:id>')
def return_book(id):
    if 'user' in session:
        conn = get_db_connection()
        conn.execute('DELETE FROM issued WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return redirect('/issued_books')
    return redirect('/login')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
