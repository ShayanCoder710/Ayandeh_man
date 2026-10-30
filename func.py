import json
import secrets
from pathlib import Path

from sqlalchemy import func as sa_func

from app import db
from models import Major, MajorRating, Question, QuestionOption, TestResult

BASE_DIR = Path(__file__).resolve().parent

CLUSTERS = {
    "math": "ریاضی و فیزیک",
    "sciences": "علوم پایه",
    "humanities": "علوم انسانی",
    "social": "علوم اجتماعی",
    "arts": "هنر و طراحی",
}

CLUSTER_BLURBS = {
    "math": "ذهن تو با منطق، تحلیل و حل مسائل فنی راحت‌تر است. خوشه‌ی ریاضی و فیزیک با دروس دقیق و کاربردی‌اش، دقیقاً برای همین سبک ذهن ساخته شده.",
    "sciences": "کنجکاوی‌ات درباره‌ی طبیعت، بدن انسان و آزمایش‌های علمی بالاست. رشته‌های علوم پایه جای مناسبی برای همین کنجکاوی و کار آزمایشگاهی‌اند.",
    "humanities": "با تحلیل متن، بحث و استدلال راحت‌تری. رشته‌های علوم انسانی روی درک عمیق جامعه و رویدادها تمرکز دارند.",
    "social": "درک رفتار آدم‌ها، کار تیمی و ارتباط با مردم برایت جذاب است. رشته‌های علوم اجتماعی همین حوزه‌ها را عمیق‌تر می‌آموزند.",
    "arts": "ذهن خلاق و بصری‌ات فعال است. خوشه‌ی هنر و طراحی فرصت می‌دهد ایده‌های تازه‌ات را به کارهای واقعی و دیدنی تبدیل کنی.",
}

_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

TRAIT_DIMS = {
    "team": "کار تیمی",
    "solo": "کار مستقل",
    "applied": "کار عملی",
    "income": "درآمدمحوری",
    "impact": "اثرگذاری اجتماعی",
    "field": "کار میدانی",
    "media": "رسانه و محتوا",
    "care": "مراقبت و خدمت",
    "leader": "رهبری",
    "logical": "تصمیم‌گیری منطقی",
    "competitive": "رقابت‌طلب",
    "stable": "ثبات شغلی",
    "calm": "محیط آرام",
    "office": "کار اداری",
}

_FA_ALPHABET = "ابپتثجحخدذرزصضطسظعغػفقکگلمنوهی"
_FA_RANK = {ch: i for i, ch in enumerate(_FA_ALPHABET)}


def fa_sort_key(text):
    key = []
    for ch in text or "":
        if ch in " ":
            continue
        key.append(_FA_RANK.get(ch, 256))
    return key


def fa_num(value):
    return str(value).replace(".", "٫").translate(_FA_DIGITS)


def cluster_name(slug):
    return CLUSTERS.get(slug, slug or "—")


def stars_html(avg):
    if avg is None:
        return "—"
    full = int(round(avg))
    inner = "".join(
        "★" if i <= full else f"<span class='off'>★</span>" for i in range(1, 6)
    )
    return f"<span class='stars'>{inner}</span>"


def difficulty_dots(n):
    inner = "".join(
        "<span class='on'></span>" if i < n else "<span></span>" for i in range(5)
    )
    return f"<span class='dots'>{inner}</span><span class='dots-label'>{fa_num(n)} از {fa_num(5)}</span>"


def load_questions():
    try:
        questions = Question.query.order_by(Question.order).all()
        return [
            {
                "id": q.id,
                "text": q.text,
                "options": [
                    {"id": o.id, "text": o.text}
                    for o in sorted(q.options, key=lambda o: o.id)
                ],
            }
            for q in questions
        ]
    except Exception:
        return []


def load_majors():
    try:
        return Major.query.order_by(Major.name).all()
    except Exception:
        return []


def get_major(slug):
    try:
        return Major.query.filter_by(slug=slug).first()
    except Exception:
        return None


def get_my_rating(slug, voter_key):
    try:
        major = Major.query.filter_by(slug=slug).first()
        if major is None:
            return None
        row = MajorRating.query.filter_by(
            major_id=major.id, voter_key=voter_key
        ).first()
        return row.score if row else None
    except Exception:
        return None


def _rating_map(major_ids):
    try:
        rows = (
            db.session.query(
                MajorRating.major_id,
                sa_func.avg(MajorRating.score),
                sa_func.count(MajorRating.id),
            )
            .filter(MajorRating.major_id.in_(major_ids))
            .group_by(MajorRating.major_id)
            .all()
        )
        return {
            row[0]: {"avg": round(float(row[1]), 1), "count": int(row[2])}
            for row in rows
        }
    except Exception:
        return {}


def get_rating(slug):
    try:
        major = Major.query.filter_by(slug=slug).first()
        if major is None:
            return {"avg": None, "count": 0}
        row = (
            db.session.query(
                sa_func.avg(MajorRating.score), sa_func.count(MajorRating.id)
            )
            .filter(MajorRating.major_id == major.id)
            .first()
        )
        if row and row[0] is not None:
            return {"avg": round(float(row[0]), 1), "count": int(row[1])}
        return {"avg": None, "count": 0}
    except Exception:
        return {"avg": None, "count": 0}


def search_majors(query="", cluster="", difficulty="", sort="popular"):
    try:
        majors = load_majors()
        if not majors:
            return []
        ratings = _rating_map([m.id for m in majors])
        entries = []
        text = (query or "").strip()
        for major in majors:
            if text and text not in major.name:
                continue
            if cluster and major.cluster != cluster:
                continue
            if difficulty:
                try:
                    if major.difficulty != int(difficulty):
                        continue
                except ValueError:
                    pass
            rating = ratings.get(major.id) or {"avg": None, "count": 0}
            entries.append(
                {
                    "major": major,
                    "avg": rating.get("avg"),
                    "count": rating.get("count", 0),
                }
            )
        if sort == "name":
            entries.sort(key=lambda e: fa_sort_key(e["major"].name))
            return entries
        entries.sort(
            key=lambda e: (
                e["avg"] is None,
                -(e["avg"] or 0),
                fa_sort_key(e["major"].name),
            )
        )
        return entries
    except Exception:
        return []


def top_majors(limit=5):
    return search_majors(sort="popular")[:limit]


def entries_for_majors(majors):
    try:
        ids = [m.id for m in majors]
        ratings = _rating_map(ids) if ids else {}
        return [
            {
                "major": m,
                "avg": (ratings.get(m.id) or {}).get("avg"),
                "count": (ratings.get(m.id) or {}).get("count", 0),
            }
            for m in majors
        ]
    except Exception:
        return []


def compare_majors(slug_a, slug_b):
    def entry(slug):
        if not slug:
            return None
        try:
            major = Major.query.filter_by(slug=slug).first()
            if major is None:
                return None
            rating = get_rating(slug)
            return {"major": major, "avg": rating["avg"], "count": rating["count"]}
        except Exception:
            return None

    return {"a": entry(slug_a), "b": entry(slug_b)}


def compare_rows(a, b):
    def rating_cell(e):
        if e is None or e["avg"] is None:
            return "هنوز رأی ندارد"
        return f"{fa_num(e['avg'])} از {fa_num(5)} ({fa_num(e['count'])} رأی)"

    return [
        {"label": "توضیح", "a": a["major"].description, "b": b["major"].description},
        {"label": "دروس اصلی", "a": a["major"].courses, "b": b["major"].courses},
        {"label": "بازار کار", "a": a["major"].job_market, "b": b["major"].job_market},
        {"label": "مزایا", "a": a["major"].pros, "b": b["major"].pros},
        {"label": "معایب", "a": a["major"].cons, "b": b["major"].cons},
        {"label": "امتیاز کاربران", "a": rating_cell(a), "b": rating_cell(b)},
    ]


def rate_major(slug, score, voter_key):
    try:
        major = Major.query.filter_by(slug=slug).first()
        if major is None:
            return "missing"
        try:
            score = int(score)
        except (TypeError, ValueError):
            return "invalid"
        if not 1 <= score <= 5:
            return "invalid"
        existing = (
            MajorRating.query.filter_by(major_id=major.id, voter_key=voter_key).first()
        )
        if existing:
            existing.score = score
        else:
            db.session.add(
                MajorRating(major_id=major.id, score=score, voter_key=voter_key)
            )
        db.session.commit()
        return "updated" if existing else "ok"
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
        return "error"


def make_token():
    return secrets.token_urlsafe(16)


def compute_result(answers):
    scores = {c: 0 for c in CLUSTERS}
    traits = {t: 0 for t in TRAIT_DIMS}

    def to_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    weights_by_option = {}
    try:
        option_ids = [
            parsed
            for parsed in (to_int(oid) for oid in (answers or {}).values())
            if parsed is not None
        ]
        if option_ids:
            options = QuestionOption.query.filter(
                QuestionOption.id.in_(option_ids)
            ).all()
            weights_by_option = {o.id: (o.weights or {}) for o in options}
    except Exception:
        weights_by_option = {}
    for _qid, oid in (answers or {}).items():
        weights = weights_by_option.get(to_int(oid))
        if not weights:
            continue
        for key, value in weights.items():
            if key in scores:
                try:
                    scores[key] += int(value)
                except (TypeError, ValueError):
                    pass
            elif key in traits:
                try:
                    traits[key] += int(value)
                except (TypeError, ValueError):
                    pass
    ordered = list(CLUSTERS)
    cluster = max(ordered, key=lambda c: (scores[c], -ordered.index(c)))
    trait_labels = [
        TRAIT_DIMS[k]
        for k, _ in sorted(
            traits.items(), key=lambda kv: (-kv[1], list(TRAIT_DIMS).index(kv[0]))
        )[:3]
        if traits[k] > 0
    ]
    major_ids = []
    try:
        cluster_majors = Major.query.filter_by(cluster=cluster).order_by(
            Major.name
        ).all()
        if cluster_majors:
            ratings = _rating_map([m.id for m in cluster_majors])
            cluster_majors.sort(
                key=lambda m: (
                    -((ratings.get(m.id) or {}).get("avg") or 0),
                    fa_sort_key(m.name),
                )
            )
        major_ids = [m.id for m in cluster_majors[:6]]
    except Exception:
        major_ids = []
    return {
        "cluster": cluster,
        "scores": scores,
        "major_ids": major_ids,
        "traits": trait_labels,
    }


def save_result(answers):
    try:
        payload = compute_result(answers)
        stored = {str(k): str(v) for k, v in (answers or {}).items()}
        stored["traits"] = payload.get("traits", [])
        record = TestResult(
            token=make_token(),
            cluster=payload["cluster"] or "",
            recommended_major_ids=payload["major_ids"],
            answers=stored,
        )
        db.session.add(record)
        db.session.commit()
        return record.token
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
        return None


def load_result(token):
    try:
        record = TestResult.query.filter_by(token=token).first()
        if record is None:
            return None
        major_ids = record.recommended_major_ids or []
        majors = (
            Major.query.filter(Major.id.in_(major_ids)).all() if major_ids else []
        )
        stored_answers = record.answers or {}
        traits = stored_answers.get("traits") or []
        if not isinstance(traits, list):
            traits = []
        return {
            "token": record.token,
            "cluster": record.cluster,
            "created_at": record.created_at,
            "majors": majors,
            "traits": [str(t) for t in traits],
        }
    except Exception:
        return None


def load_articles():
    try:
        return json.loads(
            (BASE_DIR / "data" / "articles.json").read_text(encoding="utf-8")
        )
    except Exception:
        return []


def get_article(slug):
    for article in load_articles():
        if article.get("slug") == slug:
            return article
    return None


def seed_data():
    try:
        if Question.query.count() == 0:
            questions = json.loads(
                (BASE_DIR / "data" / "questions.json").read_text(encoding="utf-8")
            )
            for order, item in enumerate(questions):
                question = Question(text=item["text"], order=order)
                for option in item.get("options", []):
                    question.options.append(
                        QuestionOption(
                            text=option["text"],
                            weights=option.get("weights", {}),
                        )
                    )
                db.session.add(question)
            db.session.commit()
        if Major.query.count() == 0:
            majors = json.loads(
                (BASE_DIR / "data" / "majors.json").read_text(encoding="utf-8")
            )
            fields = (
                "slug",
                "name",
                "cluster",
                "description",
                "courses",
                "job_market",
                "pros",
                "cons",
                "difficulty",
            )
            for item in majors:
                db.session.add(Major(**{k: item[k] for k in fields if k in item}))
            db.session.commit()
        return True
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
        return False


def _result_traits(record):
    stored = record.answers or {}
    traits = stored.get("traits") or []
    if not isinstance(traits, list):
        traits = []
    return [str(t) for t in traits]


def admin_stats():
    empty = {"total": 0, "cluster_counts": {}, "trait_counts": {}, "top_majors": []}
    try:
        records = TestResult.query.all()
        total = len(records)
        cluster_counts = {}
        trait_counts = {}
        major_counts = {}
        for record in records:
            key = record.cluster or "unknown"
            cluster_counts[key] = cluster_counts.get(key, 0) + 1
            for trait in _result_traits(record):
                trait_counts[trait] = trait_counts.get(trait, 0) + 1
            for major_id in (record.recommended_major_ids or []):
                major_counts[major_id] = major_counts.get(major_id, 0) + 1
        top_majors = []
        if major_counts:
            majors = Major.query.filter(Major.id.in_(list(major_counts))).all()
            names = {m.id: m.name for m in majors}
            top_majors = [
                {"id": mid, "name": names.get(mid, "—"), "count": count}
                for mid, count in sorted(major_counts.items(), key=lambda kv: -kv[1])
            ]
        top_cluster = max(cluster_counts.items(), key=lambda kv: kv[1])[0] if cluster_counts else ""
        top_trait = max(trait_counts.items(), key=lambda kv: kv[1])[0] if trait_counts else ""
        top_traits = [
            [label, count]
            for label, count in sorted(trait_counts.items(), key=lambda kv: -kv[1])[:6]
        ]
        return {
            "total": total,
            "cluster_counts": cluster_counts,
            "trait_counts": trait_counts,
            "top_majors": top_majors,
            "top_cluster": top_cluster,
            "top_trait": top_trait,
            "top_traits": top_traits,
        }
    except Exception:
        return empty


def recent_results(limit=30):
    try:
        records = (
            TestResult.query.order_by(TestResult.created_at.desc()).limit(limit).all()
        )
        out = []
        for record in records:
            major_names = []
            if record.recommended_major_ids:
                majors = Major.query.filter(
                    Major.id.in_(record.recommended_major_ids)
                ).all()
                major_names = [m.name for m in majors]
            out.append(
                {
                    "id": record.id,
                    "token": record.token,
                    "cluster": record.cluster,
                    "traits": _result_traits(record)[:3],
                    "majors": major_names[:3],
                    "created_at": record.created_at,
                }
            )
        return out
    except Exception:
        return []


def admin_delete_result(token):
    try:
        record = TestResult.query.filter_by(token=token).first()
        if record is None:
            return False
        db.session.delete(record)
        db.session.commit()
        return True
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
        return False
