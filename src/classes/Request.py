from flask_sqlalchemy import SQLAlchemy
from database.db import db
from enum import Enum
from etc.json import to_json
from etc.file import FileTypes

request_image_files_association = db.Table(
    'request_image_files_association',
    db.Column('request_id', db.Integer, db.ForeignKey('request.id')),
    db.Column('file_id', db.Integer, db.ForeignKey('request_file.id'))
)

request_video_files_association = db.Table(
    'request_video_files_association',
    db.Column('request_id', db.Integer, db.ForeignKey('request.id')),
    db.Column('file_id', db.Integer, db.ForeignKey('request_file.id'))
)

request_raw_files_association = db.Table(
    'request_raw_files_association',
    db.Column('request_id', db.Integer, db.ForeignKey('request.id')),
    db.Column('file_id', db.Integer, db.ForeignKey('request_file.id'))
)

request_tags_association = db.Table(
    'request_tags_association',
    db.Column('request_id', db.Integer, db.ForeignKey('request.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('request_tag.id'))
)

class RequestStatus(Enum):
    Waiting = 0
    Finished = 1
    Canceled = 2
    Expired = 3

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poster_id = db.Column(db.Integer)
    title = db.Column(db.String(50))
    description = db.Column(db.String(50))
    tags = db.relationship('RequestTag', secondary=request_tags_association, back_populates='requests')
    image_files = db.relationship('RequestFile', secondary=request_image_files_association, back_populates='requests')
    video_files = db.relationship('RequestFile', secondary=request_video_files_association, back_populates='requests')
    raw_files = db.relationship('RequestFile', secondary=request_raw_files_association, back_populates='requests')
    highest_price = db.Column(db.Integer)
    expired_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)
    modify_time = db.Column(db.DateTime)
    status = db.Column(db.Enum(RequestStatus))

    def to_json(self):
        return {
            "id": self.id,
            "poster_id": self.poster_id,
            "title": self.title,
            "description": self.description,
            "tags": [tag.name for tag in self.tags],
            "image_files": to_json(self.image_files),
            "video_files": to_json(self.video_files),
            "raw_files": to_json(self.raw_files),
            "highest_price": self.highest_price,
            "expired_time": self.expired_time,
            "create_time": self.create_time,
            "modify_time": self.modify_time,
            "status": self.status
        }

class RequestFile(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_type = db.Column(db.Enum(FileTypes))
    data = db.Column(db.LargeBinary)
    image_requests = db.relationship('Request', secondary=request_image_files_association, back_populates='image_files')
    video_requests = db.relationship('Request', secondary=request_video_files_association, back_populates='video_files')
    raw_requests = db.relationship('Request', secondary=request_raw_files_association, back_populates='raw_files')

    def to_json(self):
        return {
            "id": self.id,
            "file_type": self.file_type,
            "data": self.data
        }

class RequestTag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    requests = db.relationship('Request', secondary=request_tags_association, back_populates='tags')
