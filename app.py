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


@app.route("/")
def index():
    return render_template(
        "index.html",
        title="آینده من | راهنمای انتخاب رشته",
        description="با تست شخصیت و علاقه، خوشه و رشته تحصیلی مناسب خودت را پیدا کن.",
    )
