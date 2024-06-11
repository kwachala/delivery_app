from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from . import db


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    items = db.relationship("OrderItem", backref="order", lazy=True)
    total_price = db.Column(db.Float, nullable=False, default=0.0)


class OrderItem(db.Model):
    __tablename__ = "orderitem"  # Jawne określenie nazwy tabeli
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
