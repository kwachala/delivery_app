from flask import Flask, Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

login_registration_bp = Blueprint('login_registration', __name__)

def create_connection():
    conn = sqlite3.connect('database.db')
    return conn

@login_registration_bp.route('/')
def home():
    return render_template('index.html')


@login_registration_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        approved = 0 if role != 'klient' else 1  # Ustawiamy approved na 0, jeśli rola jest inna niż "Klient"

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role, approved) VALUES (?, ?, ?, ?)",
                       (username, password, role, approved))
        conn.commit()
        conn.close()
        return redirect(url_for('login_registration.login'))
    return render_template('register.html')


@login_registration_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            if user[4] == 0:
                session['username'] = username
                return "Twoje konto czeka na akceptację administratora."
            else:
                # todo tera tu przekierowuje kazdego ale potem to rozdzielic jakos trzeba
                session['username'] = username
                return redirect(url_for('main_menu.main_menu_client'))
        else:
            return "Błędny login lub hasło"
    return render_template('login.html')


@login_registration_bp.route('/admin')
def admin_panel():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE approved = 0")
    users = cursor.fetchall()
    conn.close()
    return render_template('admin_panel.html', users=users)


@login_registration_bp.route('/approve/<int:user_id>')
def approve_user(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET approved = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('login_registration.admin_panel'))


