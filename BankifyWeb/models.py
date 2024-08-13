# MrJ         |
# Bankify.Web |
# 7/12/2024   |
# ------------

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
import hashlib

db = SQLAlchemy()


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    transactions = db.relationship('Transaction', backref='account', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf-8'))
        self.password = sha256.hexdigest()

    def check_password(self, password):
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf-8'))
        input_password_hash = sha256.hexdigest()
        return self.password == input_password_hash


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
