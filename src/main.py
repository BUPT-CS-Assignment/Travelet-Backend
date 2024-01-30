from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from user.app import app as user
from admin.app import app as admin
from config.config import RUNTIME_HOST, RUNTIME_PORT, RUNTIME_DEBUG, AppConfig
from database.db import db

app = Flask(__name__)

app.config.from_object(AppConfig)
db.init_app(app)

app.register_blueprint(user)
app.register_blueprint(admin)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(host=RUNTIME_HOST,port=RUNTIME_PORT,debug=RUNTIME_DEBUG)