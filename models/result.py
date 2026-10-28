from datetime import datetime

from app import db


class TestResult(db.Model):
    __tablename__ = "test_result"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(40), unique=True, nullable=False, index=True)
    cluster = db.Column(db.String(50), nullable=False, default="")
    recommended_major_ids = db.Column(db.JSON, nullable=False, default=list)
    answers = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
