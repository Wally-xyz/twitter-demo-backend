from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ABI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String)
    contract_id = db.Column(db.String)
    default_metadata_hash = db.Column(db.String)
    address = db.Column(db.String)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    address = db.Column(db.String)
    private_key = db.Column(db.String)
    email = db.Column(db.String)
