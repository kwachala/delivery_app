def to_dict(self):
    return {
        'id': self.id,
        'restaurant_id': self.restaurant_id,
        'username': self.username,
        'items': self.items,
        'total_price': self.total_price,
        'status': self.status,
        'deliverer_id': self.deliverer_id
    }