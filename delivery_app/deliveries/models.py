from flask_sqlalchemy import SQLAlchemy
from . import db


class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    items = db.relationship("OrderItem", backref="order", lazy=True)
    total_price = db.Column(db.Float, nullable=False)
    deliverer_id = db.Column(db.Integer, nullable=False)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=False)


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    items = db.relationship('MenuItem', backref='menu', lazy=True)


class MenuItem(db.Model):
    __tablename__ = 'menuitem'  # Jawne określenie nazwy tabeli
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
