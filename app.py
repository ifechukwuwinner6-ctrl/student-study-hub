from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = 'university_super_secret_flash_key'

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # 1. Updated Students Table with Level
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            level TEXT NOT NULL
        )
    ''')
    # 2. Secure Mock Results Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT NOT NULL,
            course_code TEXT NOT NULL,
            score INTEGER NOT NULL,
            grade TEXT NOT NULL,
            batch_no TEXT NOT NULL,
            level TEXT NOT NULL
        )
    ''')
    # 3. Dynamic Level Chat Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT NOT NULL,
            message TEXT NOT NULL,
            level TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Insert some mock dummy results for testing if table is empty
    cursor.execute("SELECT COUNT(*) FROM results")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO results (student_email, course_code, score, grade, batch_no, level) VALUES ('student@uni.edu', 'MTH 101', 85, 'A', 'B2026', '100L')")
        cursor.execute("INSERT INTO results (student_email, course_code, score, grade, batch_no, level) VALUES ('student@uni.edu', 'PHY 101', 62, 'B', 'B2026', '100L')")
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'student_email' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', email=session['student_email'], level=session['student_level'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE email = ?', (email,))
        student = cursor.fetchone()
        conn.close()
        
        if student and check_password_hash(student[2], password):
            session['student_email'] = student[1]
            session['student_level'] = student[3] # Store level in session
            return redirect(url_for('home'))
        else:
            flash('Invalid Institutional Credentials!', 'error')
    return render_template('login.html', view='login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        level = request.form.get('level') # Capture 100L, 200L, etc.
        hashed_password = generate_password_hash(password, method='scrypt')
        
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO students (email, password, level) VALUES (?, ?, ?)', (email, hashed_password, level))
            conn.commit()
            conn.close()
            session['student_email'] = email
            session['student_level'] = level
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash('This email is already registered!', 'error')
    return render_template('login.html', view='signup')

# Secure Result Checker Route
@app.route('/checker', methods=['GET', 'POST'])
def checker():
    if 'student_email' not in session: return redirect(url_for('login'))
    results = None
    searched = False
    
    if request.method == 'POST':
        level = request.form.get('level')
        batch_no = request.form.get('batch_no')
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # Strictly matches email from current session for absolute data privacy
        cursor.execute('SELECT course_code, score, grade FROM results WHERE student_email = ? AND level = ? AND batch_no = ?', 
                       (session['student_email'], level, batch_no))
        results = cursor.fetchall()
        conn.close()
        searched = True
        
    return render_template('checker.html', results=results, searched=searched)

# Level-Based Chat Rooms Route
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'student_email' not in session: return redirect(url_for('login'))
    user_level = session['student_level']
    
    if request.method == 'POST':
        msg = request.form.get('message')
        if msg and msg.strip():
            now = datetime.datetime.now().strftime("%H:%M")
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO chats (sender_email, message, level, timestamp) VALUES (?, ?, ?, ?)',
                           (session['student_email'].split('@')[0], msg, user_level, now))
            conn.commit()
            conn.close()
            return redirect(url_for('chat'))
            
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT sender_email, message, timestamp FROM chats WHERE level = ? ORDER BY id DESC LIMIT 30', (user_level,))
    messages = cursor.fetchall()[::-1] # Reverse order to show oldest at top
    conn.close()
    
    return render_template('chat.html', messages=messages, level=user_level)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
