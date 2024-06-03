from flask_sqlalchemy import SQLAlchemy
from . import db2


class Restaurant(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True)
    name = db2.Column(db2.String(80), unique=True, nullable=False)
    address = db2.Column(db2.String(120), nullable=False)


class Menu(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True)
    restaurant_id = db2.Column(db2.Integer, db2.ForeignKey('restaurant.id'), nullable=False)
    items = db2.relationship('MenuItem', backref='menu', lazy=True)


class MenuItem(db2.Model):
    __tablename__ = 'menuitem'  # Jawne określenie nazwy tabeli
    id = db2.Column(db2.Integer, primary_key=True)
    menu_id = db2.Column(db2.Integer, db2.ForeignKey('menu.id'), nullable=False)
    name = db2.Column(db2.String(80), nullable=False)
    price = db2.Column(db2.Float, nullable=False)
