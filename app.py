from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'university_super_secret_flash_key'

# Initialize the database and create the students table if it doesn't exist
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'student_email' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', email=session['student_email'])

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
            session['student_email'] = email
            return redirect(url_for('home'))
        else:
            flash('Invalid Institutional Email or Password!', 'error')
            
    return render_template('login.html', view='login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='scrypt')
        
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO students (email, password) VALUES (?, ?)', (email, hashed_password))
            conn.commit()
            conn.close()
            session['student_email'] = email
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash('This student email is already registered!', 'error')
            
    return render_template('login.html', view='signup')

@app.route('/recover', methods=['GET', 'POST'])
def recover():
    if request.method == 'POST':
        email = request.form.get('email')
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE email = ?', (email,))
        student = cursor.fetchone()
        conn.close()
        
        if student:
            # Generate a random 6-digit recovery code
            recovery_code = str(random.randint(100000, 999999))
            flash(f'🚨 Verification Code sent to {email}: {recovery_code}', 'success')
            return render_template('login.html', view='verify', email=email, code=recovery_code)
        else:
            flash('No university account found with that email!', 'error')
            
    return render_template('login.html', view='recover')

@app.route('/logout')
def logout():
    session.pop('student_email', None)
    return redirect(url_for('login'))

# Core Faculty Vault Routes
@app.route('/library/science')
def science_library():
    if 'student_email' not in session: return redirect(url_for('login'))
    return render_template('science_library.html')

@app.route('/library/art')
def art_library():
    if 'student_email' not in session: return redirect(url_for('login'))
    return render_template('art_library.html')

@app.route('/library/commercial')
def commercial_library():
    if 'student_email' not in session: return redirect(url_for('login'))
    return render_template('commercial_library.html')

if __name__ == '__main__':
    app.run(debug=True)
