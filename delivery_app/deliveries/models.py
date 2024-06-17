from flask_sqlalchemy import SQLAlchemy
from . import db


class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), nullable=False)
    total_price = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(200), nullable=False, default="available") # available, in_progress, completed
    deliverer_id = db.Column(db.String(50), nullable=False)
    items = db.relationship("OrderItem", backref="order", lazy=True)


# class Restaurant(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), unique=True, nullable=False)
#     address = db.Column(db.String(120), nullable=False)
#
#
# class Menu(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
#     items = db.relationship('MenuItem', backref='menu', lazy=True)
#
#
class DeliveryItem(db.Model):
    __tablename__ = 'menuitem'  # Jawne określenie nazwy tabeli
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
