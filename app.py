from flask import Flask, flash, redirect, render_template, request
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
    entries_for_majors,
    fa_num,
    load_questions,
    load_result,
    save_result,
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


@app.route("/test", methods=["POST"])
def test_submit():
    questions = load_questions()
    if not questions:
        flash("هنوز سؤالی برای تست تعریف نشده است.")
        return redirect("/test")
    answers = {}
    valid_ids = set()
    for q in questions:
        option_ids = {str(o["id"]) for o in q["options"]}
        valid_ids.update(option_ids)
        answers[str(q["id"])] = request.form.get(f"q{q['id']}", "")
    if not all(answers.values()):
        flash("لطفاً به همه‌ی سؤالات پاسخ بده تا نتیجه‌ات محاسبه شود.")
        return redirect("/test")
    if any(v not in valid_ids for v in answers.values()):
        flash("برخی پاسخ‌ها معتبر نبود؛ لطفاً دوباره امتحان کن.")
        return redirect("/test")
    token = save_result(answers)
    if not token:
        flash("امکان ذخیره‌ی نتیجه نبود؛ دوباره تلاش کن.")
        return redirect("/test")
    rec = load_result(token)
    return render_template(
        "result.html",
        rec=rec,
        token=token,
        entries=entries_for_majors(rec["majors"]) if rec else [],
        title="نتیجه‌ی تست شخصیت و علاقه | آینده من",
        description="خوشه‌ی غالب و رشته‌های پیشنهادی تست شخصیت و علاقه.",
    )
