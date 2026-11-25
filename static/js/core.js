window.AM = (function () {
  var CLUSTERS = {
    riyazi: "ریاضی",
    tajrobi: "تجربی",
    ensani: "انسانی",
    fanni: "فنی‌وحرفه‌ای",
  };
  var CBLURBS = {
    riyazi: "ذهن تو با منطق، عدد و حل مسئله راحت‌تر است. رشته‌ی ریاضی (فیزیک‌ریاضی) درسی‌های محاسبه، هندسه و فیزیک دارد و مسیرِ اصلیِ مهندسی و کامپیوتر از همین‌جاست.",
    tajrobi: "کنجکاوی‌ات درباره‌ی بدن، طبیعت و آزمایش بالاست. رشته‌ی تجربی با زیست‌شناسی و شیمی پررنگ‌ترین درس‌ها را دارد و دروازه‌ی اصلیِ رشته‌های پزشکی و سلامت است.",
    ensani: "با متن، بحث و اندیشیدن درباره‌ی آدم‌ها و جامعه راحت‌تری. رشته‌ی انسانی سرشار از ادبیات، تاریخ، جامعه‌شناسی و منطق است؛ سبک‌تر از تجربی و ریاضی و با مسیرِ رشته‌های علوم انسانی.",
    fanni: "دست‌ات حسابی به‌کار می‌رود و کارِ عملی و ساختن و تعمیر کردن برایت جذاب است. فنی‌وحرفه‌ای رشته‌های کاربردی دارد و با دیپلمِ فنی می‌توانی زودتر وارد بازار کار شوی.",
  };
  var TRAITS = {
    team: "کار تیمی",
    solo: "کار مستقل",
    applied: "کار عملی",
    income: "درآمدمحوری",
    impact: "اثرگذاری اجتماعی",
    field: "کار میدانی",
    media: "رسانه و محتوا",
    care: "مراقبت و خدمت",
    leader: "رهبری",
    logical: "تصمیم‌گیری منطقی",
    competitive: "رقابت‌طلب",
    stable: "ثبات شغلی",
    calm: "محیط آرام",
    office: "کار اداری",
  };
  var CLUSTER_ORDER = ["riyazi", "tajrobi", "ensani", "fanni"];
  var cache = {};

  function loadJSON(path) {
    if (cache[path]) return Promise.resolve(cache[path]);
    return fetch(path, { cache: "no-cache" })
      .then(function (r) {
        if (!r.ok) throw new Error("http " + r.status);
        return r.json();
      })
      .then(function (data) {
        cache[path] = data;
        return data;
      });
  }

  var FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
  function faNum(value) {
    return String(value).replace(/\d/g, function (d) {
      return FA_DIGITS[+d];
    });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  var FA_ALPHA = "ابپتثجحخدذرزصضطسظعغػفقکگلمنوهی";
  var FA_RANK = {};
  FA_ALPHA.split("").forEach(function (ch, i) {
    FA_RANK[ch] = i;
  });
  function cmpFa(a, b) {
    var ka = (a || "").split("");
    var kb = (b || "").split("");
    var rank = function (ch) {
      return ch === " " ? null : FA_RANK.hasOwnProperty(ch) ? FA_RANK[ch] : 256;
    };
    for (var i = 0; i < Math.max(ka.length, kb.length); i++) {
      var x = i < ka.length ? rank(ka[i]) : null;
      var y = i < kb.length ? rank(kb[i]) : null;
      if (x === y) continue;
      if (x === null) return -1;
      if (y === null) return 1;
      return x - y;
    }
    return 0;
  }

  function norm(text) {
    return (text || "").replace(/\u200c/g, "").toLowerCase();
  }

  function param(name) {
    return new URLSearchParams(location.search).get(name);
  }

  function icon(name, cls) {
    return (
      '<svg class="bi ' + (cls || "").trim() + '" aria-hidden="true"><use href="static/icons/am-sprite.svg#' +
      name + '"></use></svg>'
    );
  }

  function starsHtml(n) {
    if (!n) return "—";
    var full = Math.round(n);
    var s = "";
    for (var i = 1; i <= 5; i++) {
      s += i <= full ? "★" : "<span class='off'>★</span>";
    }
    return "<span class='stars'>" + s + "</span>";
  }

  function dotsHtml(n) {
    var s = "";
    for (var i = 0; i < 5; i++) {
      s += i < n ? "<span class='on'></span>" : "<span></span>";
    }
    return "<span class='dots'>" + s + "</span><span class='dots-label'>" + faNum(n) + " از " + faNum(5) + "</span>";
  }

  function questions() {
    return loadJSON("data/questions.json");
  }

  function majors() {
    return loadJSON("data/majors.json");
  }

  function mainArticles() {
    return loadJSON("data/articles.json");
  }

  function subtrackArticles() {
    return loadJSON("data/subtracks_articles.json");
  }

  function allArticles() {
    return Promise.all([mainArticles(), subtrackArticles()]).then(function (xs) {
      return xs[0].concat(xs[1]);
    });
  }

  function subtrackMap() {
    return loadJSON("data/subtrack_slug_map.json");
  }

  function majorBySlug(slug) {
    return majors().then(function (list) {
      for (var i = 0; i < list.length; i++) {
        if (list[i].slug === slug) return list[i];
      }
      return null;
    });
  }

  function subsOf(major) {
    return subtrackMap().then(function (map) {
      var names = Array.isArray(major.sub_tracks) ? major.sub_tracks : [];
      return names.map(function (n) {
        return { name: n, slug: map[n] || null };
      });
    });
  }

  function articleBySlug(slug) {
    return allArticles().then(function (list) {
      for (var i = 0; i < list.length; i++) {
        if (list[i].slug === slug) return list[i];
      }
      return null;
    });
  }

  function getRating(slug) {
    try {
      var v = localStorage.getItem("am-rating-" + slug);
      return v ? +v : null;
    } catch (e) {
      return null;
    }
  }

  function setRating(slug, n) {
    try {
      if (n) localStorage.setItem("am-rating-" + slug, String(n));
    } catch (e) {}
  }

  function ratingCell(slug) {
    var r = getRating(slug);
    if (!r) return "هنوز امتیازی نداده‌ای";
    return starsHtml(r) + " " + faNum(r) + " از " + faNum(5);
  }

  function scoreAnswers(answers, qs) {
    var scores = { riyazi: 0, tajrobi: 0, ensani: 0, fanni: 0 };
    var traits = {};
    Object.keys(TRAITS).forEach(function (k) {
      traits[k] = 0;
    });
    Object.keys(answers || {}).forEach(function (qi) {
      var q = qs[qi];
      var o = q && q.options[+answers[qi]];
      if (!o) return;
      Object.keys(o.weights || {}).forEach(function (k) {
        var v = +o.weights[k] || 0;
        if (k in scores) scores[k] += v;
        else if (k in traits) traits[k] += v;
      });
    });
    var cluster = CLUSTER_ORDER[0];
    CLUSTER_ORDER.forEach(function (c) {
      if (scores[c] > scores[cluster]) cluster = c;
    });
    var topTraits = Object.keys(traits)
      .filter(function (k) {
        return traits[k] > 0;
      })
      .sort(function (a, b) {
        return traits[b] - traits[a] || Object.keys(TRAITS).indexOf(a) - Object.keys(TRAITS).indexOf(b);
      })
      .slice(0, 3)
      .map(function (k) {
        return TRAITS[k];
    });
    return { scores: scores, cluster: cluster, traits: topTraits };
  }

  function encodeAnswers(answers) {
    var s = Object.keys(answers)
      .sort(function (a, b) {
        return a - b;
      })
      .map(function (k) {
        return k + ":" + answers[k];
      })
      .join(",");
    return btoa(s);
  }

  function decodeAnswers(d) {
    try {
      var out = {};
      atob(d).split(",").forEach(function (p) {
        if (!p) return;
        var kv = p.split(":");
        out[kv[0]] = +kv[1];
      });
      return out;
    } catch (e) {
      return null;
    }
  }

  function faceoffQuestions(qs, a, b, count) {
    var score = function (q) {
      return (q.options || []).reduce(function (sum, o) {
        var w = o.weights || {};
        return sum + Math.min((+w[a] || 0) + (+w[b] || 0), 4);
      }, 0);
    };
    return qs
      .map(function (q, i) {
        return { q: q, i: i, s: score(q) };
      })
      .sort(function (x, y) {
        return y.s - x.s;
      })
      .slice(0, count || 12)
      .map(function (x) {
        return x.i;
      });
  }

  function faceoffScore(answers, qs, a, b) {
    var scoreA = 0;
    var scoreB = 0;
    var reasons = [];
    Object.keys(answers || {}).forEach(function (qi) {
      var q = qs[qi];
      var o = q && q.options[+answers[qi]];
      if (!q || !o) return;
      var w = o.weights || {};
      var wa = +w[a] || 0;
      var wb = +w[b] || 0;
      scoreA += wa;
      scoreB += wb;
      var diff = wa - wb;
      if (diff !== 0) {
        reasons.push({ question: q.text, winner: diff > 0 ? a : b, strength: Math.abs(diff) });
      }
    });
    reasons.sort(function (x, y) {
      return y.strength - x.strength;
    });
    var total = scoreA + scoreB;
    if (total === 0) return { pctA: 50, pctB: 50, tie: true, reasons: [] };
    return {
      pctA: Math.round((scoreA * 100) / total),
      pctB: Math.round((scoreB * 100) / total),
      tie: scoreA === scoreB,
      reasons: reasons.slice(0, 3),
    };
  }

  function searchAll(text, data) {
    var majorsList = data.majors;
    var map = data.subtrackMap;
    var articles = data.articles;
    var t = norm(text);
    var result = { majors: [], subtracks: [], articles: [] };
    if (!t) return result;
    majorsList.forEach(function (m) {
      var subs = (Array.isArray(m.sub_tracks) ? m.sub_tracks : []).map(function (n) {
        return { name: n, slug: map[n] || null };
      });
      var hit = norm(m.name).indexOf(t) !== -1 || subs.some(function (s) {
        return norm(s.name).indexOf(t) !== -1;
      });
      if (hit) {
        result.majors.push({
          major: m,
          match_subs: subs.filter(function (s) {
            return norm(s.name).indexOf(t) !== -1;
          }).map(function (s) {
            return s.name;
          }),
        });
      }
    });
    var seen = {};
    articles.forEach(function (a) {
      if (seen[a.slug]) return;
      seen[a.slug] = true;
      var title = norm(a.title);
      var summary = norm(a.summary || "");
      if (a.subtrack_parent && title.indexOf(t) !== -1) result.subtracks.push(a);
      else if (!a.subtrack_parent && (title.indexOf(t) !== -1 || summary.indexOf(t) !== -1)) result.articles.push(a);
    });
    return result;
  }

  function subChipHtml(sub) {
    if (sub.slug) {
      return '<a class="sub-chip" href="article.html?slug=' + encodeURIComponent(sub.slug) + '">' + sub.name + "</a>";
    }
    return '<span class="sub-chip">' + sub.name + "</span>";
  }

  function majorCardHtml(e) {
    var m = e.major;
    var rating = getRating(m.slug);
    var meta = rating
      ? starsHtml(rating) + " <span>امتیاز تو: " + faNum(rating) + "</span>"
      : "<span>هنوز امتیازی نداده‌ای</span>";
    var subPreview = e.sub_preview ? "<p class='card-sub'>" + e.sub_preview + "</p>" : "";
    return (
      '<article class="major-card reveal">' +
      '<div class="badge-row"><span class="badge">رشته‌ی دبیرستانی</span></div>' +
      "<h3><a href=\"major.html?slug=" + m.slug + '">' + m.name + "</a></h3>" +
      '<div class="card-meta">' + meta + " <span>·</span> " + dotsHtml(+m.difficulty || 3) + "</div>" +
      subPreview +
      "</article>"
    );
  }

  function articleCardHtml(a) {
    var badge = a.subtrack_parent ? '<span class="article-subtrack">مقاله‌ی زیررشته</span>' : "";
    return (
      '<article class="article-card reveal">' +
      '<span class="article-minutes">' + icon("clock") + faNum(a.minutes) + " دقیقه مطالعه</span> " +
      badge +
      "<h3><a href=\"article.html?slug=" + a.slug + '">' + a.title + "</a></h3>" +
      "<p>" + (a.summary || "") + "</p>" +
      '<a class="article-link" href="article.html?slug=' + a.slug + '">خواندن مقاله ←</a>' +
      "</article>"
    );
  }

  return {
    CLUSTERS: CLUSTERS,
    CBLURBS: CBLURBS,
    CLUSTER_ORDER: CLUSTER_ORDER,
    escapeHtml: escapeHtml,
    cmpFa: cmpFa,
    questions: questions,
    majors: majors,
    mainArticles: mainArticles,
    subtrackArticles: subtrackArticles,
    allArticles: allArticles,
    subtrackMap: subtrackMap,
    majorBySlug: majorBySlug,
    subsOf: subsOf,
    articleBySlug: articleBySlug,
    getRating: getRating,
    setRating: setRating,
    ratingCell: ratingCell,
    faNum: faNum,
    norm: norm,
    param: param,
    icon: icon,
    starsHtml: starsHtml,
    dotsHtml: dotsHtml,
    scoreAnswers: scoreAnswers,
    encodeAnswers: encodeAnswers,
    decodeAnswers: decodeAnswers,
    faceoffQuestions: faceoffQuestions,
    faceoffScore: faceoffScore,
    searchAll: searchAll,
    subChipHtml: subChipHtml,
    majorCardHtml: majorCardHtml,
    articleCardHtml: articleCardHtml,
  };
})();
