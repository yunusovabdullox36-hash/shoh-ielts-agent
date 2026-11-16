# -*- coding: utf-8 -*-
"""Build an IELTSSHOKH Authentic Reading HTML (1 passage or full 3-passage test)
from prepared, validated data."""
import re, json
from pathlib import Path
from .icons import ic
from . import promo
from .common import brand_logo, brand_welcome

A = Path(__file__).resolve().parents[1] / "assets"
rd = lambda f: (A / f).read_text(encoding="utf-8")

def build(D):
    t = rd("reading_base.html")
    QT, AN = D.QT, D.AN
    ACCEPT = getattr(D, "ACCEPT", {})
    passages = D.PASSAGES
    multi_p = len(passages) > 1

    def between(a, b):
        i = t.index(a); return t[i:t.index(b, i)]

    def ev(s):
        return re.sub(r"\{\{(\d+)\|(.+?)\}\}", lambda m: '<span class="ans-ev" data-q="%s">%s</span>' % (m.group(1), m.group(2)), s, flags=re.S)

    # ---- question numbers per passage ----
    def sec_qs(s):
        if s["type"] == "multi": return list(range(s["q"], s["q"] + s.get("n", 2)))
        if s["type"] == "notes": return [int(x) for x in re.findall(r"\[\[(\d+)\]\]", s["html"])]
        return list(s["qs"])
    groups = []
    for p in passages:
        qs = [q for s in p["sections"] for q in sec_qs(s)]
        groups.append([min(qs), max(qs)])
    allq = [q for g in groups for q in range(g[0], g[1] + 1)]
    total = len(allq)
    for q in allq:
        assert q in AN, "AN missing Q%d" % q
        assert q in QT, "QT missing Q%d" % q
    minutes = getattr(D, "MINUTES", 20 * len(passages))

    # ---- head ----
    css_end = t.index("</style>")
    head = t[:css_end] + rd("extra.css") + rd("fullscreen.css") + "</style>\n</head>\n"
    head = re.sub(r"<title>.*?</title>", lambda _: "<title>IELTS Reading — %s | IELTSSHOKH</title>" % D.TITLE, head, count=1, flags=re.S)

    welcome = between("<!-- WELCOME -->", "<!-- HEADER -->")
    welcome = welcome.replace("Start Passage →", ("Start Test → (%d min)" % minutes) if multi_p else "Start Passage →")
    welcome = welcome.replace("</button>", '</button><div class="fs-hint">The test opens in full screen. Press F11 to leave or re-enter it.</div>', 1) if 'class="welcome-start"' in welcome else welcome

    header = between("<!-- HEADER -->", '<div id="progress-wrap">')
    sub = "<span>Academic · Passage 1</span><span>· Q1–13</span>"
    assert sub in header
    label = "Full Reading Test" if multi_p else "Passage %d" % passages[0]["num"]
    header = header.replace(sub, "<span>Academic · %s</span><span>· Q%d–%d · %d min</span>" % (label, allq[0], allq[-1], minutes))
    header = header.replace(">20:00<", ">%02d:00<" % minutes)
    fs_btn = ('<button class="hd-fs" id="fs-btn" data-shkh-fs title="Full screen (F11)" aria-label="Full screen">'
              '<span class="fs-on">%s</span><span class="fs-off">%s</span><span class="fs-label">Full screen</span></button>\n    ') % (ic("expand", solo=True), ic("shrink", solo=True))
    assert '<button class="theme-toggle"' in header
    header = header.replace('<button class="theme-toggle"', fs_btn + '<button class="theme-toggle"', 1)

    modal = between("<!-- RESULT MODAL -->", "<script>")
    modal = modal.replace("Your Result — Passage 1", "Your Result — " + label).replace(">0/13<", ">0/%d<" % total)
    modal = modal.replace('<div class="band-feedback"', '<div class="rb-secs" id="rb-secs"></div>\n      <div class="band-feedback"', 1)

    tip = between('<div class="vault-tip">', '<div class="analysis-heading">Question-by-question')
    cta = between('<a class="vault-cta', '\n')
    an_head = between('<div class="analysis-heading">', '<table class="para-table">')

    # ---- passages ----
    def passage_sec(i, p):
        out = ['<div class="psec%s" id="psec%d"><div class="passage-card-body">' % (" on" if i == 0 else "", i),
               '<div class="passage-label">Reading Passage %d</div>' % p["num"],
               '<div class="passage-heading">%s</div>' % p["title"],
               '<div class="passage-caption"><em>%s</em></div>' % p["caption"],
               '<div class="passage-body">']
        for para in p["paras"]:
            if para.startswith("##"): out.append('<h4 class="p-sub">%s</h4>' % para[2:])
            elif para.startswith("@@"): out.append("<p><em>%s</em></p>" % ev(para[2:]))
            elif re.match(r"^[A-Z]\|", para): out.append('<p><span class="para-letter">%s</span>%s</p>' % (para[0], ev(para[2:])))
            else: out.append("<p>%s</p>" % ev(para))
        out.append("</div></div></div>")
        return "\n".join(out)

    # ---- questions ----
    def head_block(s):
        return '<div class="section-block">\n<div class="section-label">%s</div>\n<div class="section-desc">%s</div>\n' % (s["label"], s["desc"])
    def tfng(n, vals):
        b = "".join('<button class="tfng-btn" data-val="%s">%s</button>' % (v, v) for v in vals)
        return '<div class="q-card" data-q="%d" data-type="tfng"><div class="q-row"><span class="q-n">%d</span><span class="q-text">%s</span></div><div class="tfng-group">%s</div></div>\n' % (n, n, QT[n], b)
    def chip(n, letters):
        c = "".join('<span class="chip-opt" data-opt="%s" tabindex="0">%s</span>' % (l, l) for l in letters)
        return ('<div class="q-card" data-q="%d" data-type="chip"><div class="q-row"><span class="q-n">%d</span><span class="q-text">%s</span></div>'
                '<div class="q-row-chip" style="padding-left:40px;margin-top:8px"><div class="chip-picker">%s</div></div></div>\n') % (n, n, QT[n], c)
    def mc(n, opts):
        o = "".join('<div class="mc-opt" data-opt="%s" tabindex="0">%s</div>' % (l, x) for l, x in opts)
        return '<div class="q-card" data-q="%d" data-type="mc"><div class="q-row"><span class="q-n">%d</span><span class="q-text">%s</span></div><div class="mc-opts">%s</div></div>\n' % (n, n, QT[n], o)
    def inp(n):
        return ('<span class="q-card q-card-inline" data-q="%d" data-type="text"><input class="ti-input" data-q="%d" type="text" autocomplete="off" '
                'spellcheck="false" placeholder="%d" style="width:130px;"></span>') % (n, n, n)

    def render(s):
        h = head_block(s)
        ty = s["type"]
        if ty in ("tfng", "ynng"):
            vals = ["TRUE", "FALSE", "NOT GIVEN"] if ty == "tfng" else ["YES", "NO", "NOT GIVEN"]
            h += "".join(tfng(n, vals) for n in s["qs"])
        elif ty == "notes":
            body = re.sub(r"\[\[(\d+)\]\]", lambda m: inp(int(m.group(1))), s["html"])
            h += '<div class="note-box"><div class="note-box-title">%s</div><div class="note-txt" style="line-height:2.6">%s</div></div>' % (s.get("title", ""), body)
        elif ty == "multi":
            q = s["q"]
            o = "".join('<div class="multi-opt" data-opt="%s" tabindex="0">%s</div>' % (l, x) for l, x in s["options"])
            nn = s.get("n", 2)
            h += ('<div class="q-card" data-q="%d" data-qs="%s" data-n="%d" data-type="multi"><div class="q-row"><span class="q-n pair">%d&ndash;%d</span>'
                  '<span class="q-text"><i>%s</i></span></div><div class="multi-opts">%s</div></div>\n') % (q, " ".join(str(q + i) for i in range(nn)), nn, q, q + nn - 1, s["stem"], o)
        elif ty == "chip":
            if s.get("box"): h += '<div class="pbox">%s</div>\n' % s["box"]
            h += "".join(chip(n, s["letters"]) for n in s["qs"])
        elif ty == "mc":
            h += "".join(mc(n, s["options"][n]) for n in s["qs"])
        else:
            raise SystemExit("unknown section type " + ty)
        return h + "</div>\n"

    passages_html = "\n".join(passage_sec(i, p) for i, p in enumerate(passages))
    questions_html = "\n".join('<div class="qgroup%s" id="qg%d">%s</div>' % (" on" if i == 0 else "", i, "".join(render(s) for s in p["sections"]))
                               for i, p in enumerate(passages))
    analysis = ('<div id="analysis-section">\n' + an_head +
                '<table class="para-table"><thead><tr><th>Q</th><th>Keyword in the question</th><th>Paraphrase in the passage</th></tr></thead>'
                '<tbody id="kw-body"></tbody></table>\n' + tip +
                '<div class="analysis-heading">Question-by-question feedback</div>\n<div id="fb-list"></div>\n' + cta +
                '\n</div>\n<div style="height:40px"></div>')
    layout = ('<div id="layout">\n<div id="passage-panel">\n%s\n</div>\n<div id="resize-handle"></div>\n<div id="questions-panel">\n%s\n%s\n</div>\n</div>\n'
              % (passages_html, questions_html, analysis))
    tabs = "".join('<button class="ptab%s" onclick="setPassage(%d)"><span class="pt-long">Passage </span><span class="pt-short">P</span>%d</button>' % (" on" if i == 0 else "", i, p["num"]) for i, p in enumerate(passages))
    left = '<div class="ptabs">%s</div>' % tabs if multi_p else '<span class="ft-active-label">Passage %d</span>' % passages[0]["num"]
    footer = ('<div id="footer-bar">\n%s\n<div id="ft-center"></div>\n<div id="footer-actions"><button class="nav-arr" id="nav-prev" onclick="navQ(-1)">‹</button>'
              '<button class="nav-arr" id="nav-next" onclick="navQ(1)">›</button></div>\n</div>\n' % left)
    footer += between('<button id="hl-btn">', "\n") + "\n"

    # ---- data for JS ----
    ANS = {q: AN[q][0] for q in allq}
    PAIR = {}
    for p in passages:
        for s in p["sections"]:
            if s["type"] == "multi":
                PAIR[s["q"]] = ",".join(sorted(AN[s["q"] + i][0] for i in range(s.get("n", 2))))
    acc = {q: [a.lower() for a in ACCEPT.get(q, [AN[q][0]])] for q in allq}
    KW = {q: [AN[q][1], AN[q][2]] for q in allq}
    FB = {q: {"verd": AN[q][0], "stmt": QT[q], "ev": AN[q][3], "ex": AN[q][4]} for q in allq}
    ICONS = {"check": ic("check"), "x": ic("x"), "chev": ic("chevron", solo=True), "key": ic("key")}

    hl_js = t[t.index("/* ================= HIGHLIGHT"):t.index("/* ================= SUBMIT")]
    js = rd("reading_engine.js")
    j = lambda obj: json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")
    values = {"__ANS__": j(ANS), "__ACCEPT__": j(acc), "__QNUMS__": j(allq),
              "__GROUPS__": j(groups), "__PAIR__": j(PAIR), "__KW__": j(KW),
              "__FB__": j(FB), "__ICONS__": j(ICONS), "__MINUTES__": str(minutes),
              "__HL__": hl_js}
    js = re.sub("|".join(values), lambda match: values[match[0]], js)
    vault = t[t.index("/* ====== SYNONYMS VAULT link"):t.index("</script>", t.index("/* ====== SYNONYMS VAULT link"))]

    head, header = brand_logo(head, header)
    head, welcome = brand_welcome(head, welcome)
    html = (head + '<body class="light">\n\n' + welcome + header + '<div id="progress-wrap"><div id="progress-bar"></div></div>\n'
            + layout + footer + modal + "<script>\n" + rd("fullscreen.js") + "\n" + js + "\n" + vault + "</script>\n</body></html>\n")
    html, _n = promo.swap(html)
    return html
