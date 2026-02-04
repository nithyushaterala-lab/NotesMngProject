from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "myverysecretkey"

# --------------------
# Database Connection
# --------------------
def get_db_connection():
    conn = sqlite3.connect("notes.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# --------------------
# Home
# --------------------
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/viewall')
    return redirect('/login')

# --------------------
# Register
# --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if not username or not email or not password:
            flash("Please fill all fields.", "danger")
            return redirect('/register')

        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            flash("Username already taken.", "danger")
            conn.close()
            return redirect('/register')

        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_pw)
        )
        conn.commit()
        conn.close()

        flash("Registration successful! Please log in.", "success")
        return redirect('/login')

    return render_template('register.html')

# --------------------
# Login
# --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash("Please enter username and password.", "danger")
            return redirect('/login')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome, {user['username']}!", "success")
            return redirect('/viewall')

        flash("Invalid username or password.", "danger")
        return redirect('/login')

    return render_template('login.html')

# --------------------
# Logout
# --------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect('/login')

# --------------------
# Add Note
# --------------------
@app.route('/addnote', methods=['GET', 'POST'])
def addnote():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()

        if not title or not content:
            flash("Title and content cannot be empty.", "danger")
            return redirect('/addnote')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notes (title, content, user_id) VALUES (?, ?, ?)",
            (title, content, session['user_id'])
        )
        conn.commit()
        conn.close()

        flash("Note added successfully.", "success")
        return redirect('/viewall')

    return render_template('addnote.html')

# --------------------
# View All Notes
# --------------------
@app.route('/viewall')
def viewall():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, content, created_at FROM notes WHERE user_id = ? ORDER BY created_at DESC",
        (session['user_id'],)
    )
    notes = cur.fetchall()
    conn.close()

    return render_template('viewnotes.html', notes=notes)

# --------------------
# View Single Note
# --------------------
@app.route('/viewnotes/<int:note_id>')
def viewnotes(note_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session['user_id'])
    )
    note = cur.fetchone()
    conn.close()

    if not note:
        flash("Note not found.", "danger")
        return redirect('/viewall')

    return render_template('singlenote.html', note=note)

# --------------------
# Update Note
# --------------------
@app.route('/updatenote/<int:note_id>', methods=['GET', 'POST'])
def updatenote(note_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, content FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session['user_id'])
    )
    note = cur.fetchone()

    if not note:
        conn.close()
        flash("Note not found or unauthorized.", "danger")
        return redirect('/viewall')

    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()

        if not title or not content:
            flash("Title and content required.", "danger")
            return render_template('updatenote.html', note=note)

        cur.execute(
            "UPDATE notes SET title = ?, content = ? WHERE id = ? AND user_id = ?",
            (title, content, note_id, session['user_id'])
        )
        conn.commit()
        conn.close()

        flash("Note updated.", "success")
        return redirect('/viewall')

    conn.close()
    return render_template('updatenote.html', note=note)

# --------------------
# Delete Note
# --------------------
@app.route('/deletenote/<int:note_id>', methods=['POST'])
def deletenote(note_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session['user_id'])
    )
    conn.commit()
    conn.close()

    flash("Note deleted.", "info")
    return redirect('/viewall')

# --------------------
# About Page
# --------------------
@app.route('/about')
def about():
    return render_template('about.html')

# --------------------
# Contact Page
# --------------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash("Message sent successfully!", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')

# --------------------
# Footer Year
# --------------------
@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}

# --------------------
# Run App
# --------------------
if __name__ == '__main__':
    app.run(debug=True)

