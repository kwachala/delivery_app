from flask import Flask
import sqlite3
from login_registration import login_registration_bp
from main_menu import main_menu_bp
app = Flask(__name__)
app.secret_key = "secret_key"


def create_connection():
    conn = sqlite3.connect('database.db')
    return conn


def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            approved INTEGER DEFAULT 0
        );
    ''')
    conn.commit()
    conn.close()


create_table()

app.register_blueprint(login_registration_bp)
app.register_blueprint(main_menu_bp)

if __name__ == '__main__':
    app.run(debug=True)
