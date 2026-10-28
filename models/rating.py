from datetime import datetime

from app import db


class MajorRating(db.Model):
    __tablename__ = "major_rating"

    id = db.Column(db.Integer, primary_key=True)
    major_id = db.Column(db.Integer, db.ForeignKey("major.id"), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False, default=5)
    voter_key = db.Column(db.String(64), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    major = db.relationship("Major", back_populates="ratings")
