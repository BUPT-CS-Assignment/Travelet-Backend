from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(AppConfig)
db = SQLAlchemy()
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()