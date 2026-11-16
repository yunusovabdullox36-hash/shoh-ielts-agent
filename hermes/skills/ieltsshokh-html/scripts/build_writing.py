# -*- coding: utf-8 -*-
"""Build an IELTSSHOKH Writing HTML in the SAME skin as the Authentic Reading test
(white CDI look, red IELTS logo on the left, IELTSSHOKH on the right, blue accents, navy dark mode).
"""
import re, json
from pathlib import Path
from .icons import ic
from . import promo
from .common import brand_logo, brand_welcome
A = Path(__file__).resolve().parents[1] / "assets"
rd = lambda f: (A / f).read_text(encoding="utf-8")


def build(D):
    t = rd("reading_base.html")
    between = lambda a, b: t[t.index(a):t.index(b, t.index(a))]

    css_end = t.index("</style>")
    head = t[:css_end] + rd("extra.css") + rd("fullscreen.css") + rd("writing.css") + "</style>\n</head>\n"
    head = re.sub(r"<title>.*?</title>", lambda _: "<title>IELTS %s | IELTSSHOKH</title>" % D.LABEL_HTML, head, count=1, flags=re.S)
    logo = re.search(r'class="wl-img" src="([^"]+)"', t).group(1)

    # ---- welcome: same dark card, plus session picker ----
    welcome = between("<!-- WELCOME -->", "<!-- HEADER -->")
    start = '<button class="welcome-start" onclick="startTest()">Start Passage →</button>'
    assert start in welcome
    picker = ('<div class="w-modes">'
              '<button class="w-mode on" data-mode="full"><span><b>Full test</b><small>Task 1 and Task 2</small></span><span class="t">60:00</span></button>'
              '<button class="w-mode" data-mode="t1"><span><b>Task 1 only</b><small>Report</small></span><span class="t">20:00</span></button>'
              '<button class="w-mode" data-mode="t2"><span><b>Task 2 only</b><small>Essay</small></span><span class="t">40:00</span></button></div>'
              '<label class="w-practice"><span class="sw"><input type="checkbox" id="practice"><i></i></span><span class="w-pt"><b>Practice mode</b><small>Unlocks the Band 8 toolkit. Leave it off for real exam conditions.</small></span></label>'
              '<button class="welcome-start" onclick="startTest()">Start Writing →</button>'
              '<button class="welcome-start hidden" id="resume-btn" type="button">Resume draft</button>'
              '<div class="fs-hint">The test opens in full screen. Press F11 to leave or re-enter it.</div>')
    welcome = welcome.replace(start, picker)

    # ---- header: IELTS Academic on the left, IELTSSHOKH stays on the right (as in Reading) ----
    header = between("<!-- HEADER -->", '<div id="progress-wrap">')
    sub = "<span>Academic · Passage 1</span><span>· Q1–13</span>"
    assert sub in header
    header = header.replace(sub, '<span id="hd-sub">Academic · Writing</span>')
    header = header.replace(">20:00<", ">60:00<")
    fs_btn = ('<button class="hd-fs" id="fs-btn" data-shkh-fs title="Full screen (F11)" aria-label="Full screen">'
              '<span class="fs-on">%s</span><span class="fs-off">%s</span><span class="fs-label">Full screen</span></button>\n    ') % (ic("expand", solo=True), ic("shrink", solo=True))
    kit_btn = '<button class="hd-kit" id="kit-btn" title="Band 8 toolkit">%sToolkit</button>\n    ' % ic("wrench")
    size = '<span class="hd-size"><button id="fs-down" title="Smaller text" aria-label="Smaller text">A-</button><button id="fs-up" title="Larger text" aria-label="Larger text">A+</button></span>\n    '
    k = '<button class="theme-toggle"'
    assert k in header
    header = header.replace(k, kit_btn + size + fs_btn + k, 1)

    # ---- layout ----
    views = ""
    for n in sorted(D.TASKS):
        T = D.TASKS[n]
        if T.get("source_image"):
            chart = ('<div class="chart-card"><img src="%s" alt="Original Writing Task 1 visual" '
                     'style="display:block;width:100%%;height:auto"></div>') % T["source_image"]
        else:
            chart = '<div class="chart-card">%s</div>' % T["chart_svg"] if T.get("chart_svg") else ""
        views += ('<div class="task-view%s" id="prompt-%d"><div class="passage-heading">%s</div>'
                  '<div class="passage-caption"><em>%s</em></div><div class="prompt-box">%s</div>%s</div>\n') % (
                  " on" if n == 1 else "", n, T["title"], T["inst"], T["prompt_html"], chart)
    layout = ('<!-- LAYOUT -->\n<div id="layout">\n  <div id="passage-panel"><div class="passage-card-body">\n'
              '    <div class="passage-label">Writing <span id="mode-tag" class="w-tag">Exam mode</span></div>\n' + views +
              '    <details class="plan"><summary>Notes</summary><textarea id="plan" placeholder="Overview, ideas, examples..." spellcheck="false" aria-label="Planning notes"></textarea></details>\n'
              '  </div></div>\n  <div id="resize-handle" title="Drag to resize"></div>\n'
              '  <div id="questions-panel" class="editor">\n'
              '    <textarea id="essay" placeholder="Start writing your response here..." spellcheck="false" autocomplete="off" autocorrect="off" autocapitalize="off" aria-label="Your response"></textarea>\n'
              '    <div class="wbar" id="wbar"><i></i></div>\n'
              '    <div class="wstats"><span class="wn"><span id="wc">0</span> <small>/ <span id="wmin">150</span> words</small></span><span class="wl" id="wc-l">Keep building</span>'
              '<span class="wm"><span>Paragraphs <b id="pc">0</b></span><span>Sentences <b id="sc">0</b></span></span></div>\n'
              '  </div>\n</div>\n')

    footer = ('<!-- FOOTER -->\n<div id="footer-bar">\n  <span class="ft-active-label">Writing</span>\n'
              '  <div class="ptabs"><button class="ptab on" data-part="1">Task 1</button><button class="ptab" data-part="2">Task 2</button></div>\n'
              '  <div id="ft-center" class="wft"></div>\n  <span id="saved-t">Auto-save on</span>\n</div>\n')

    kit = ('<aside id="kit" aria-label="Band 8 toolkit"><div class="kit-head"><h3>Band 8 toolkit<button id="kit-close" aria-label="Close toolkit">×</button></h3>'
           '<p>Tap a phrase to insert it at your cursor.</p></div><div class="kit-body" id="kit-body"></div></aside>\n')

    # ---- promo blocks copied from the Reading base (rule: never remove them) ----
    pick = lambda pat: re.search(pat, t, re.S).group(0)
    rb_vault = pick(r'<a class="rb-vault[^>]*>.*?</a>')
    rb_speak = pick(r'<a class="rb-speaking[^>]*>.*?</a>').replace("Your Reading is on track", "Your Writing is on track")
    vault_tip = pick(r'<div class="vault-tip">.*?</div>').replace("Spotting these paraphrases is the difference between Band 6 and Band 8", "Precise, varied vocabulary is the difference between Band 6 and Band 8")
    vault_cta = pick(r'<a class="vault-cta[^>]*>.*?</a>')
    assert "Writing is on track" in rb_speak
    # Writing wording (the Reading copy talks about Reading answers)
    vault_tip = ('<div class="vault-tip">Want to improve your English even further? <a class="js-vault-link" href="https://t.me/ieltsshokh" target="_blank" rel="noopener">Jump into our channel →</a></div>')
    vault_cta = re.sub(r"<h3>.*?</h3>", lambda m: "<h3>Repeated words quietly cost you marks.</h3>", vault_cta, count=1, flags=re.S)
    vault_cta = re.sub(r"<p>.*?</p>", lambda m: "<p>Vocabulary range is a quarter of your Writing score. The <b>Synonyms Vault</b> is a ready-made collection of <b>1500+ real exam paraphrases</b>, sorted by topic and question type, so you can vary your wording with confidence.</p>", vault_cta, count=1, flags=re.S)

    confirm = ('<div class="wmodal" id="confirm" role="dialog" aria-modal="true"><div class="result-box">'
               '<div class="rb-head"><h2>Submit your writing?</h2><button class="rb-close" data-close="confirm" aria-label="Close">×</button></div>'
               '<div class="rb-body"><div id="cf-rows"></div><p class="cf-note">You will not be able to edit your answers after submitting.</p>'
               '<div class="rb-btns"><button class="secondary" data-close="confirm">Keep writing</button><button class="primary" id="cf-yes">Submit</button></div></div></div></div>\n')
    result = ('<!-- RESULT MODAL -->\n<div id="result-modal"><div class="result-box">'
              '<div class="rb-head"><h2 id="res-h">Writing submitted</h2><button class="rb-close" onclick="closeResult()">×</button></div>'
              '<div class="rb-body"><div id="res-cards"></div><div class="band-feedback">Your teacher will check your writing.</div>'
              + rb_vault + rb_speak +
              '<div class="rb-btns"><button class="secondary" id="pdf-btn">Download PDF</button><button class="primary" onclick="reviewAnswers()">Review answers &amp; analysis →</button></div>'
              '</div></div></div>\n')
    review = ('<div id="review"><div class="rv-bar"><h2>Review and model answers</h2><div id="rv-tabs"></div>'
              '<button class="rv-btn" id="rv-new">New attempt</button><button class="rv-btn" id="rv-close">Close</button></div>'
              '<div class="rv-body"><div class="rv-grid" id="rv-grid"></div><div class="rv-promo">' + vault_tip + vault_cta + '</div></div></div>\n')

    icons = {"check": ic("check", solo=True), "x": ic("x", solo=True), "pen": ic("pen"), "book": ic("book"), "warn": ic("alert")}
    test = {"id": D.ID, "label": D.LABEL, "tasks": {str(n): {k: v for k, v in T.items() if k not in ("chart_svg", "source_image", "prompt_html")} for n, T in D.TASKS.items()}}
    j = lambda obj: json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")
    values = {"__TEST__": j(test), "__KIT__": j(D.KIT), "__ICONS__": j(icons), "__LOGO__": j(logo)}
    js = re.sub("|".join(values), lambda match: values[match[0]], rd("writing_engine.js"))
    jspdf = rd("jspdf.umd.min.js").replace("</script", "<" + "/script")
    head, header = brand_logo(head, header)
    head, welcome = brand_welcome(head, welcome)
    html = (head + '<body class="light">\n\n' + welcome + header + '<div id="progress-wrap"><div id="progress-bar"></div></div>\n' + layout + footer + kit + confirm + result + review +
            "<script>\n" + jspdf + "\n</script>\n<script>\n" + rd("fullscreen.js") + "\n" + js + "\n</script>\n</body></html>\n")
    html, _n = promo.swap(html)
    return html
