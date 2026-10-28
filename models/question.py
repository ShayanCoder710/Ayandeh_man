from app import db


class Question(db.Model):
    __tablename__ = "question"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)

    options = db.relationship(
        "QuestionOption", back_populates="question", cascade="all, delete-orphan"
    )


class QuestionOption(db.Model):
    __tablename__ = "question_option"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    weights = db.Column(db.JSON, nullable=False, default=dict)

    question = db.relationship("Question", back_populates="options")
