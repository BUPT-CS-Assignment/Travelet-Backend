from flask_sqlalchemy import SQLAlchemy
from database.db import db

class SuccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer)
    poster_id = db.Column(db.Integer)
    responder_id = db.Column(db.Integer)
    poster_cost = db.Column(db.Integer)
    responder_cost = db.Column(db.Integer)
    deal_time = db.Column(db.DateTime)

    def to_json(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "poster_id": self.poster_id,
            "responder_id": self.responder_id,
            "poster_cost": self.poster_cost,
            "responder_cost": self.responder_cost,
            "deal_time": self.deal_time
        }

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    month = db.Column(db.Integer)
    location = db.Column(db.String(50))
    amount=  db.Column(db.Integer)
    profit = db.Column(db.Integer)

    def to_json(self):
        return {
            "id": self.id,
            "month": self.month,
            "location": self.location,
            "amount": self.amount,
            "profit": self.profit
        }