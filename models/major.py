from datetime import datetime

from app import db


class Major(db.Model):
    __tablename__ = "major"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    cluster = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False, default="")
    courses = db.Column(db.Text, nullable=False, default="")
    job_market = db.Column(db.Text, nullable=False, default="")
    pros = db.Column(db.Text, nullable=False, default="")
    cons = db.Column(db.Text, nullable=False, default="")
    sub_tracks = db.Column(db.Text, nullable=False, default="")
    difficulty = db.Column(db.Integer, nullable=False, default=3)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    ratings = db.relationship(
        "MajorRating", back_populates="major", cascade="all, delete-orphan"
    )
