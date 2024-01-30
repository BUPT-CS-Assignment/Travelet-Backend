from flask_sqlalchemy import SQLAlchemy
from database.db import db
from enum import Enum
from etc.json import to_json
from etc.file import FileTypes

response_image_files_association = db.Table(
    'response_image_files_association',
    db.Column('response_id', db.Integer, db.ForeignKey('response.id')),
    db.Column('file_id', db.Integer, db.ForeignKey('response_file.id'))
)

response_video_files_association = db.Table(
    'response_video_files_association',
    db.Column('response_id', db.Integer, db.ForeignKey('response.id')),
    db.Column('file_id', db.Integer, db.ForeignKey('response_file.id'))
)

response_raw_files_association = db.Table(
    'response_raw_files_association',
    db.Column('response_id', db.Integer, db.ForeignKey('response.id')),
    db.Column('file_id', db.Integer, db.ForeignKey('response_file.id'))
)

class ResponseStatus(Enum):
    Waiting = 0
    Accepted = 1
    Denied = 2
    Canceled = 3

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer)
    responder_id = db.Column(db.Integer)
    description = db.Column(db.String(50))
    image_files = db.relationship('ResponseFile', secondary=response_image_files_association, back_populates='responses')
    video_files = db.relationship('ResponseFile', secondary=response_video_files_association, back_populates='responses')
    raw_files = db.relationship('ResponseFile', secondary=response_raw_files_association, back_populates='responses')
    create_time = db.Column(db.DateTime)
    modify_time = db.Column(db.DateTime)
    status = db.Column(db.Enum(ResponseStatus))

    def to_json(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "responder_id": self.responder_id,
            "description": self.description,
            "files": to_json(self.files),
            "create_time": self.create_time,
            "modify_time": self.modify_time,
            "status": self.status
        }

class ResponseFile(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_type = db.Column(db.Enum(FileTypes))
    data = db.Column(db.LargeBinary)
    image_responses = db.relationship('Response', secondary=response_image_files_association, back_populates='image_files')
    video_responses = db.relationship('Response', secondary=response_video_files_association, back_populates='video_files')
    raw_responses = db.relationship('Response', secondary=response_raw_files_association, back_populates='raw_files')

    def to_json(self):
        return {
            "id": self.id,
            "file_type": self.file_type,
            "data": self.data
        }