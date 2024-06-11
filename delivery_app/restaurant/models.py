from sqlalchemy import event
from flask_sqlalchemy import SQLAlchemy
from . import db


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    cuisine = db.Column(db.String(60), nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )  # active, inactive, pending
    owner_id = db.Column(db.Integer, nullable=False)
    menu = db.relationship("Menu", backref="restaurant", lazy=True, uselist=False)


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), nullable=False
    )
    items = db.relationship(
        "MenuItem", backref="menu", lazy=True, cascade="all, delete-orphan"
    )


class MenuItem(db.Model):
    __tablename__ = "menuitem"  # Jawne określenie nazwy tabeli
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)


class AwaitingOrder(db.Model):
    __tablename__ = "awaitingorder"  # Jawne określenie nazwy tabeli
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
