# -*- coding: utf-8 -*-
"""Synonyms ad. RULE (owner, 2026-11-06): in the result modal after EVERY submit the Synonyms ad is a COMPACT strip built like the
Speaking strip below it (same height/layout), with assets/synonyms_banner.webp (the shokh Synonyms Vault picture) as its dimmed
background. NOT a big image, NO animations. swap(html) replaces the old text-only .rb-vault card with it and adds the css once.
The review-page .vault-cta text block is left alone (Writing rewords it; Reading keeps its Reading copy)."""
import base64, re
from pathlib import Path
A = Path(__file__).resolve().parents[1] / "assets"
URL = "https://t.me/ieltsshokh/4007"
KEY = ('<svg class="ic solo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
       '<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/></svg>')
CSS = """:root{--syn-img:url("data:image/webp;base64,@@B64@@")}
.syn-strip{display:flex;align-items:center;gap:12px;background:linear-gradient(90deg,rgba(5,20,70,.97) 0%,rgba(5,20,70,.92) 58%,rgba(5,20,70,.5) 100%),var(--syn-img) right center/cover;border-radius:12px;padding:12px 15px;margin-bottom:16px;text-decoration:none}
/* calm: no blue glow, no hover lift, icons always white (they vanished on dark) */
.syn-strip,.rb-speaking{box-shadow:0 2px 8px rgba(0,0,0,.28)!important}
.syn-strip:hover,.rb-speaking:hover{box-shadow:0 2px 8px rgba(0,0,0,.28)!important;transform:none!important}
.syn-strip .rb-speaking-ic,.rb-speaking .rb-speaking-ic{color:#fff!important}
.syn-strip .rb-speaking-ic svg,.rb-speaking .rb-speaking-ic svg{stroke:#fff!important}
body.dark .rb-btns .secondary{color:#cbd5e1;border-color:#334155}
.syn-go{font-size:.8rem;font-weight:800;color:#1e3a8a;background:#fff;padding:8px 13px;border-radius:9px;white-space:nowrap;flex-shrink:0}
"""


def css():
    b64 = base64.b64encode((A / "synonyms_banner.webp").read_bytes()).decode("ascii")
    return CSS.replace("@@B64@@", b64)


def banner():
    return ('<a class="syn-strip js-vault-link" href="%s" target="_blank" rel="noopener"><span class="rb-speaking-ic">%s</span>'
            '<span class="rb-speaking-tx"><b>Every answer was hidden behind a synonym</b><span>1500+ real exam paraphrases - Synonyms Pack</span></span>'
            '<span class="syn-go">Open &rarr;</span></a>') % (URL, KEY)


def swap(html):
    html, n = re.subn(r'<a class="rb-vault[^"]*"[^>]*>.*?</a>', lambda m: banner(), html, flags=re.S)
    assert n >= 1, "no result-modal Synonyms strip (.rb-vault) found to replace"
    assert "</style>\n</head>" in html
    return html.replace("</style>\n</head>", css() + "</style>\n</head>", 1), n
