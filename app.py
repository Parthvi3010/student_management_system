import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    if search_query:
        students = conn.execute(
            'SELECT * FROM students WHERE name LIKE ? OR roll_no LIKE ?',
            (f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('index.html', students=students, search_query=search_query)

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        course = request.form['course']

        if not name or not roll_no or not course:
            return render_template('add.html', error="All fields are required.")

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO students (name, roll_no, course) VALUES (?, ?, ?)',
                         (name, roll_no, course))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('add.html', error="Roll number already exists.")
        
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()

    if student is None:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        course = request.form['course']

        if not name or not roll_no or not course:
            return render_template('edit.html', student=student, error="All fields are required.")

        try:
            conn.execute('UPDATE students SET name = ?, roll_no = ?, course = ? WHERE id = ?',
                         (name, roll_no, course, id))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('edit.html', student=student, error="Roll number already exists.")

        conn.close()
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('edit.html', student=student)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)