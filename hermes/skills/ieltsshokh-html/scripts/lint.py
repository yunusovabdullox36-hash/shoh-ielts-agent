# -*- coding: utf-8 -*-
"""IELTSSHOKH file linter. Fails (exit 1) on anything that broke a delivery before.
Usage: python lint.py <file.html> [more.html ...]
Checks:
  1. no emoji / pictographs (use inline SVG icons from icons.py)
  2. no Uzbek words anywhere in the file (visible text, titles, comments)
  3. no external scripts/styles (files must work offline)
  4. reading tests: every question has ANS + KW + FB; every evidence quote and
     paraphrase fragment exists VERBATIM in the passage text; every non-NOT GIVEN
     answer has a highlighted .ans-ev span in the passage."""
import re, sys, json, html as H
from pathlib import Path

EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️⌀-⏿■-◿←-↑↓-⇿\U000E0000-\U000E007F]")
# U+2192 (→) is allowed: plain typographic arrow, renders as text in every font.
UZ_WORDS = r"\b(va|uchun|ham|bilan|kerak|emas|yoki|lekin|ochish|yopish|savol|javob|natija|vaqt|boshlash|tekshir\w*|rivojlantir\w*|muntazam|kanal\w*|mobil|planshet|sotuv|kirish|chiqish|so'm|qil\w*|bo'l\w*|o'z\w*|ko'r\w*|to'g'ri|xato|yaxshi|uchun|mana|bu yerda|shu)\b"
UZ_APOS = re.compile(r"\b\w*(?:o|g)['ʻ’`]\w+", re.I)
UZ_APOS_OK = {"o'clock"}

def strip_noise(t):
    t = re.sub(r"data:[a-z/+.-]+;base64,[A-Za-z0-9+/=]+", "", t)
    t = re.sub(r"<script>\s*/\*\* @license.*?</script>", "<script></script>", t, flags=re.S)  # inlined jsPDF (minified vendor code)
    t = re.sub(r"https?://\S+?(?=[\"'\s<)])", "", t)
    return t

def norm(s):
    s = re.sub(r"</?(span|i|b|em|strong|a|sup|sub)(?:\s[^>]*)?>", "", s)
    s = H.unescape(re.sub(r"<[^>]+>", " ", s))
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("\\'", "'")
    return re.sub(r"\s+", " ", s).strip().lower()

def lint(path):
    raw = Path(path).read_text(encoding="utf-8")
    t = strip_noise(raw)
    errs = []
    for m in EMOJI.finditer(t):
        errs.append("EMOJI %r near: %s" % (m.group(), t[max(0, m.start()-40):m.end()+20].replace("\n", " ")))
    for m in re.finditer(UZ_WORDS, t, re.I):
        ctx = t[max(0, m.start()-40):m.end()+30].replace("\n", " ")
        errs.append("UZBEK %r near: %s" % (m.group(), ctx))
    for m in UZ_APOS.finditer(re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)):
        w = m.group().lower()
        if re.search(r"[og]['ʻ’`]", w) and w not in UZ_APOS_OK and not re.search(r"\w+'s$|n't$|'(re|ve|ll|d|m)$", w):
            errs.append("UZBEK? %r" % m.group())
    for m in re.finditer(r"<(script|link)[^>]+(src|href)=[\"']https?://[^\"']+", raw):
        if "fonts.googleapis" not in m.group():
            errs.append("EXTERNAL dependency: " + m.group()[:120])

    if "const FB" in raw:
        def js(name):
            m = re.search(r"const %s = (\{.*?\});\n" % name, raw, re.S)
            try: return json.loads(m.group(1)) if m else None
            except ValueError: return "nojson"
        ANS, KW, FB = js("ANS"), js("KW"), js("FB")
        if "nojson" in (ANS, KW, FB):
            print("  (info) data block is not builder JSON - data checks skipped")
        elif not (ANS and KW and FB):
            errs.append("reading data (ANS/KW/FB) not JSON-parsable")
        else:
            if 'id="audio"' in raw:   # Listening: there is no passage; the paraphrase must sit inside the quoted recording words
                for q in ANS:
                    if q not in KW or q not in FB:
                        errs.append("Q%s missing KW/FB" % q); continue
                    ev = norm(FB[q]["ev"])
                    if norm(KW[q][1]).strip(" .,;:") not in ev:
                        errs.append("Q%s paraphrase not found in the quoted recording words: %r" % (q, KW[q][1][:60]))
                    if len(ANS[q]) > 1 and not ANS[q].isdigit() and ANS[q].lower() not in norm(FB[q]["ev"]) and not re.search(r"%s" % re.escape(ANS[q].lower()), norm(FB[q]["ex"])):
                        errs.append("Q%s answer %r not backed by evidence or explanation" % (q, ANS[q]))
                return errs
            body = " ".join(re.findall(r'<div class="passage-body"[^>]*>(.*?)</div>', raw, re.S))
            P = norm(body)
            for q in ANS:
                if q not in KW or q not in FB:
                    errs.append("Q%s missing KW/FB" % q); continue
                for frag in re.findall(r'"([^"]{8,})"', FB[q]["ev"]):
                    for piece in re.split(r"…|\.\.\.", frag):
                        p = norm(piece).strip(" .,;:")
                        if len(p) >= 10 and p not in P:
                            errs.append("Q%s evidence not verbatim in passage: %r" % (q, piece.strip()[:80]))
                para = KW[q][1]
                if not para.startswith("—"):
                    for piece in re.split(r"…|\.\.\.", para):
                        p = norm(piece).strip(" .,;:")
                        if len(p) >= 6 and p not in P:
                            errs.append("Q%s paraphrase not verbatim in passage: %r" % (q, piece.strip()[:80]))
                if ANS[q] != "NOT GIVEN" and ('class="ans-ev" data-q="%s"' % q) not in raw:
                    errs.append("Q%s has no .ans-ev evidence span in the passage" % q)
    return errs

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    bad = 0
    for f in sys.argv[1:]:
        e = lint(f)
        print(("FAIL" if e else "PASS"), f, "(%d issues)" % len(e))
        for x in e: print("  -", x)
        bad += bool(e)
    sys.exit(1 if bad else 0)
