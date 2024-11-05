from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class VisitorHistory(db.Model):
    __tablename__ = 'visitor_history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_address = db.Column(db.String(45), nullable=True)
    visit_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Visitor {self.ip_address} at {self.visit_timestamp}>'

class LoggedUsers(db.Model):
    __tablename__ = 'logged_users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_number = db.Column(db.String(30), nullable=False)
    local_storage = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<LoggedUser {self.username} from {self.ip_address}>'
