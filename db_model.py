from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Instance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instance_name = db.Column(db.String(255), unique=True, nullable=False)
    port = db.Column(db.Integer, unique=True, nullable=False)
    pid = db.Column(db.Integer)
    status = db.Column(db.String(50), nullable=False)
    folder = db.Column(db.String(255), nullable=False)
    install_path = db.Column(db.String(255), nullable=False)
    min_memory = db.Column(db.String(50))
    max_memory = db.Column(db.String(50))
    ip_address = db.Column(db.String(50), default='localhost')