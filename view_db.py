import sqlite3


def view_database_restaurant():
    conn = sqlite3.connect('instance/restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM restaurant")
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        print(row)


def view_database_menu():
    conn = sqlite3.connect('instance/restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        print(row)

def view_database_menu_item():
    conn = sqlite3.connect('instance/restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menuitem")
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        print(row)

def view_tables():
    conn = sqlite3.connect('instance/restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    conn.close()

view_tables()
