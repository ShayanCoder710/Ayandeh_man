from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

import config

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = config.MYSQL_CONFIG
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

import models

from func import (
    CLUSTER_BLURBS,
    cluster_name,
    difficulty_dots,
    fa_num,
    load_questions,
    seed_data,
    stars_html,
    top_majors,
)

with app.app_context():
    db.create_all()
    seed_data()


@app.context_processor
def inject_helpers():
    return {
        "cluster_name": cluster_name,
        "stars_html": stars_html,
        "difficulty_dots": difficulty_dots,
        "fa_num": fa_num,
        "CLUSTER_BLURBS": CLUSTER_BLURBS,
    }


@app.route("/")
def index():
    return render_template(
        "index.html",
        top=top_majors(5),
        title="آینده من | راهنمای انتخاب رشته",
        description="با تست شخصیت و علاقه، خوشه و رشته تحصیلی مناسب خودت را پیدا کن.",
    )


@app.route("/test", methods=["GET"])
def test_page():
    return render_template(
        "test.html",
        questions=load_questions(),
        title="تست شخصیت و علاقه | آینده من",
        description="دوازده سؤال کوتاه؛ در پایان خوشه‌ی غالب و رشته‌های پیشنهادی‌ات را ببین.",
    )
