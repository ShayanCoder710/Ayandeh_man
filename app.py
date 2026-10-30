import functools
import secrets

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
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
    CLUSTERS,
    CLUSTER_BLURBS,
    admin_delete_result,
    admin_stats,
    cluster_name,
    compare_majors,
    compare_rows,
    difficulty_dots,
    entries_for_majors,
    fa_num,
    get_article,
    get_major,
    get_my_rating,
    get_rating,
    load_articles,
    load_majors,
    load_questions,
    load_result,
    rate_major,
    recent_results,
    save_result,
    search_majors,
    seed_data,
    stars_html,
    top_majors,
)

try:
    with app.app_context():
        db.create_all()
        seed_data()
except Exception:
    print("database unavailable; starting in degraded mode")


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


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
        top=top_majors(6),
        articles_preview=load_articles()[:3],
        title="آینده من | راهنمای انتخاب رشته",
        description="با تست شخصیت و علاقه، خوشه و رشته تحصیلی مناسب خودت را پیدا کن.",
    )


@app.route("/test", methods=["GET"])
def test_page():
    return render_template(
        "test.html",
        questions=load_questions(),
        title="تست شخصیت و علاقه | آینده من",
        description="سؤالات کوتاهی از تو؛ در پایان خوشه‌ی غالب و رشته‌های پیشنهادی‌ات را ببین.",
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
        share_url=url_for("result_page", token=token, _external=True),
        entries=entries_for_majors(rec["majors"]) if rec else [],
        title="نتیجه‌ی تست شخصیت و علاقه | آینده من",
        description="خوشه‌ی غالب و رشته‌های پیشنهادی تست شخصیت و علاقه.",
    )


@app.route("/result/<token>")
def result_page(token):
    rec = load_result(token)
    return render_template(
        "result.html",
        rec=rec,
        token=token,
        share_url=request.url,
        entries=entries_for_majors(rec["majors"]) if rec else [],
        title="نتیجه‌ی تست شخصیت و علاقه | آینده من",
        description="نتیجه‌ی ذخیره‌شده‌ی تست شخصیت و علاقه؛ خوشه‌ی غالب و رشته‌های پیشنهادی.",
    )


@app.route("/majors")
def majors_page():
    query = request.args.get("q", "").strip()
    cluster = request.args.get("cluster", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    sort = request.args.get("sort", "popular")
    if sort not in ("popular", "name"):
        sort = "popular"
    return render_template(
        "majors.html",
        entries=search_majors(query, cluster, difficulty, sort),
        query=query,
        cluster=cluster,
        difficulty=difficulty,
        sort=sort,
        clusters=CLUSTERS,
        title="مشاهده رشته‌ها | آینده من",
        description="جستجو و فیلتر رشته‌های تحصیلی بر اساس خوشه، سختی و محبوبیت.",
    )


def _voter_key():
    key = session.get("voter_key")
    if not key:
        key = secrets.token_hex(16)
        session["voter_key"] = key
    return key


@app.route("/majors/<slug>")
def major_page(slug):
    major = get_major(slug)
    if major is None:
        abort(404)
    rating = get_rating(slug)
    my_rating = get_my_rating(slug, _voter_key())
    return render_template(
        "major.html",
        major=major,
        rating=rating,
        my_rating=my_rating,
        title=f"{major.name} | آینده من",
        description=f"توضیحات، دروس، بازار کار و امتیازات رشته‌ی {major.name}.",
    )


@app.route("/rate/<slug>", methods=["POST"])
def rate_page(slug):
    major = get_major(slug)
    if major is None:
        flash("رشته‌ای با این نشانی پیدا نشد.")
        return redirect("/majors")
    try:
        score = int(request.form.get("score", ""))
    except ValueError:
        score = 0
    status = rate_major(slug, score, _voter_key())
    if status in ("ok", "updated"):
        flash(f"امتیازت برای {major.name} ثبت شد. ممنون از مشارکت‌ات!")
    elif status == "invalid":
        flash("امتیاز معتبر نیست؛ عددی بین ۱ تا ۵ انتخاب کن.")
    elif status == "missing":
        flash("رشته‌ای با این نشانی پیدا نشد.")
    else:
        flash("امتیازت ذخیره نشد؛ دوباره تلاش کن.")
    return redirect(f"/majors/{slug}")


@app.route("/compare")
def compare_page():
    a = request.args.get("a", "").strip()
    b = request.args.get("b", "").strip()
    majors = load_majors()
    options = [
        {"slug": m.slug, "name": m.name} for m in majors
    ]
    data = compare_majors(a, b) if a and b else {"a": None, "b": None}
    rows = (
        compare_rows(data["a"], data["b"])
        if data["a"] and data["b"]
        and data["a"]["major"].slug != data["b"]["major"].slug
        else []
    )
    return render_template(
        "compare.html",
        data=data,
        rows=rows,
        options=options,
        a=a,
        b=b,
        title="مقایسه رشته‌ها | آینده من",
        description="دو رشته تحصیلی را انتخاب کن و جنبه‌های کلیدی‌شان را کنار هم ببین.",
    )


@app.route("/guide")
def guide_page():
    return render_template(
        "guide.html",
        title="راهنمای انتخاب رشته | آینده من",
        description="چند نکته‌ی عملی برای انتخاب رشته؛ از شناخت خودت تا مقایسه‌ی دو رشته.",
    )


@app.route("/articles")
def articles_page():
    return render_template(
        "articles.html",
        articles=load_articles(),
        title="مقالات انتخاب رشته | آینده من",
        description="مقالات کوتاه درباره‌ی انتخاب رشته: علاقه در برابر بازار کار، خطاهای رایج و مسیرهای تکمیلی.",
    )


@app.route("/articles/<slug>")
def article_page(slug):
    article = get_article(slug)
    if article is None:
        abort(404)
    others = [a for a in load_articles() if a["slug"] != slug][:3]
    return render_template(
        "article.html",
        article=article,
        others=others,
        title=f"{article['title']} | آینده من",
        description=article["summary"],
    )


def require_admin(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapper


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if secrets.compare_digest(username, config.ADMIN_USERNAME) and secrets.compare_digest(
            password, config.ADMIN_PASSWORD
        ):
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("نام کاربری یا رمز عبور نادرست است.")
    return render_template(
        "admin/login.html",
        title="ورود ادمین | آینده من",
        description="ورود به پنل مدیریت آینده من.",
    )


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    flash("از پنل ادمین خارج شدی.")
    return redirect(url_for("index"))


@app.route("/admin")
@require_admin
def admin_dashboard():
    stats = admin_stats()
    results = recent_results(30)
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        results=results,
        clusters=CLUSTERS,
        title="پنل ادمین | آینده من",
        description="پایش نتایج تست شخصیت و علاقه.",
    )


@app.route("/admin/results/<token>/delete", methods=["POST"])
@require_admin
def admin_delete(token):
    removed = admin_delete_result(token)
    if removed:
        flash("نتیجه حذف شد.")
    else:
        flash("نتیجه پیدا نشد یا حذف نشد.")
    return redirect(url_for("admin_dashboard"))
