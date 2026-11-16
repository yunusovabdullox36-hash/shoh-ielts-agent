# -*- coding: utf-8 -*-
"""Shared by build_reading.py and build_writing.py (one look for every IELTSSHOKH HTML)."""
import re, struct, base64, os

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def brand_logo(head, header):
    """Header sh|kh mark and the word IELTSSHOKH must be ONE colour: navy (#1e3a8a) in light mode, white in dark mode.
    The mark is drawn as a CSS mask so it can take any colour."""
    m = re.search(r'<img class="hd-logo-img2" src="(data:image/png;base64,[^"]+)"[^>]*>', header)
    assert m, "header logo <img> not found"
    uri = m.group(1)
    logo = base64.b64decode(uri.split(",", 1)[1])
    if logo[:8] != b"\x89PNG\r\n\x1a\n" or logo[12:16] != b"IHDR":
        raise ValueError("Invalid bundled PNG logo")
    w, h = struct.unpack(">II", logo[16:24])
    r = w / h
    css = (":root{--shkh-logo:url(\"%s\")}\n"
           ".hd-logo-mask{display:block;flex-shrink:0;height:30px;width:%.3fpx;background:#1e3a8a;-webkit-mask:var(--shkh-logo) center/contain no-repeat;mask:var(--shkh-logo) center/contain no-repeat}\n"
           "body.dark .hd-logo-mask{background:#fff}body.dark .hd-shokh-txt{color:#fff}\n"
           "@media(max-width:860px){.hd-logo-mask{height:26px;width:%.3fpx}}\n") % (uri, 30 * r, 26 * r)
    header = header.replace(m.group(0), '<span class="hd-logo-mask" role="img" aria-label="IELTSSHOKH"></span>')
    # header channel button: the channel is not only synonyms -> "MAIN GRID" with the Telegram plane icon
    hb = ('<a class="vault-btn" href="https://t.me/ieltsshokh" target="_blank" rel="noopener" title="MAIN GRID - our Telegram channel">'
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>'
          'MAIN GRID<span class="vault-arrow"><svg class="ic solo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg></span></a>')
    header, nb = re.subn(r'<a class="vault-btn[^>]*>.*?</a>', lambda m: hb, header, count=1, flags=re.S)
    assert nb == 1, "header vault button not found"
    return head.replace("</style>", css + "</style>", 1), header


def brand_welcome(head, welcome):
    """Welcome card: logo + the IELTSSHOKH word stay; the t.me link pill is removed (owner's decision 2026-11-06)."""
    pat = r'<div><a class="welcome-tg".*?</a></div>'
    assert 'welcome-brand-link' in welcome
    return head, re.sub(pat, '', welcome, count=1, flags=re.S)  # no-op when the base has no pill
