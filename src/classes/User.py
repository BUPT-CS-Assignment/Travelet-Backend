from flask_sqlalchemy import SQLAlchemy
from database.db import db
from sqlalchemy.orm import validates
import re

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean)
    name = db.Column(db.String(50))
    certificate_type = db.Column(db.String(50))
    certificate_number = db.Column(db.String(50))
    telephone = db.Column(db.String(11))
    level = db.Column(db.Integer)
    description = db.Column(db.String(50))
    register_city = db.Column(db.String(50))
    register_time = db.Column(db.DateTime)
    modify_time = db.Column(db.DateTime)
    cost = db.Column(db.Integer)

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "is_admin": self.is_admin,
            "name": self.name,
            "certificate_type": self.certificate_type,
            "certificate_number": self.certificate_number,
            "telephone": self.telephone,
            "level": self.level,
            "description": self.description,
            "register_city": self.register_city,
            "register_time": self.register_time,
            "modify_time": self.modify_time,
            "cost": self.cost
        }

    @validates('telephone')
    def validate_telephone(self, key, value):
        # 检查长度是否为11
        if len(value) != 11:
            raise ValueError('Telephone must be 11 digits long.')
        
        # 使用正则表达式检查值是否只包含数字
        if not re.match(r'^\d+$', value):
            raise ValueError('Telephone must contain only digits.')

        return value
