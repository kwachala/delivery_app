from flask import Flask, Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

main_menu_bp = Blueprint('main_menu', __name__)

@main_menu_bp.route('/main_menu_client')
def main_menu_client():
    return render_template('main_menu_client.html', username=session['username'])
