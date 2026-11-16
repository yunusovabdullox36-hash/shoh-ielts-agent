"""Bounded incremental FTS5 index for an explicitly scoped Markdown corpus."""

from contextlib import closing
from hashlib import sha256
from pathlib import Path
import re
import sqlite3


SOURCE_NAMES = ("decisions.md", "channel-profile.md", "audience.md", "brand-voice.md", "shoh-workflows.md")
ALLOWED_STATUS = {"active", "approved", "verified"}
HEADING = re.compile(r"^#{1,6}\s+(.+)")
WORD = re.compile(r"[^\W_]+", re.UNICODE)
INDEX_VERSION = 2
CHUNK_SIZE = 1100
ALIASES = {
    "tasdiq": ("approval", "approved"),
    "tasdiqlash": ("approval", "approved"),
    "nashr": ("publication", "publishing"),
    "e'lon": ("publication", "publishing"),
    "auditoriya": ("audience",),
    "uslub": ("voice", "tone"),
    "qoralama": ("draft",),
    "reviziya": ("revision",),
    "obunachi": ("subscribers",),
    "rang": ("color", "palette"),
    "brend": ("brand",),
    "til": ("language",), "tilda": ("language",), "tilni": ("language",), "tili": ("language",),
}
# Uzbek is agglutinative: "kanalda", "obunachilar", "ranglari" must reach "kanal", "obunachi", "rang".
# Longest suffix first; the stem is searched as an FTS5 prefix token.
SUFFIXES = ("laringizni", "larimizni", "lardagi", "laridan", "larini", "larida", "lariga", "lardan",
            "larga", "larni", "lari", "lar", "dagi", "ning", "imiz", "ingiz", "ni", "ga", "dan", "da",
            "si", "i")
MIN_STEM = 4


def stem(word):
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= MIN_STEM:
            return word[:-len(suffix)]
    return word


def sections(body, first_line):
    heading = ""
    block = []
    start = first_line
    last = first_line
    size = 0
    for line_number, line in enumerate(body.splitlines(), first_line):
        match = HEADING.match(line)
        if match or size + len(line) + bool(block) > CHUNK_SIZE:
            if any(item.strip() for item in block):
                yield heading, start, last, "\n".join(block).strip()
            block, size, start = [], 0, line_number
        if match:
            heading = match.group(1)[:150]
        # Preserve every segment of long source lines and its original citation.
        # Prefer word boundaries so tokens crossing the hard boundary remain searchable.
        while len(line) > CHUNK_SIZE:
            cut = line.rfind(" ", CHUNK_SIZE // 2, CHUNK_SIZE + 1)
            cut = cut + 1 if cut != -1 else CHUNK_SIZE
            yield heading, line_number, line_number, line[:cut].strip()
            line = line[cut:]
        if not block:
            start = line_number
        block.append(line)
        size += len(line) + int(len(block) > 1)
        last = line_number
    if any(item.strip() for item in block):
        yield heading, start, last, "\n".join(block).strip()


def approved_snapshot(root):
    if not root.is_dir():
        raise FileNotFoundError("Knowledge directory is unavailable")
    result = {}
    for name in SOURCE_NAMES:
        source = root / name
        if not source.is_file() or source.is_symlink() or source.resolve().parent != root:
            continue
        with source.open("rb") as handle:
            raw = handle.read(65_537)
        if len(raw) > 65_536:
            continue
        lines = raw.decode("utf-8-sig").splitlines()
        if not lines or lines[0] != "---" or "---" not in lines[1:]:
            continue
        end = lines.index("---", 1)
        status = next((line.split(":", 1)[1].strip() for line in lines[1:end]
                       if line.startswith("status:")), "")
        if status in ALLOWED_STATUS:
            result[name] = (sha256(raw).hexdigest(), "\n".join(lines[end + 1:]), end + 2)
    return result


def search(root: Path, database: Path, query, limit=4):
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 300:
        raise ValueError("Query must be 1–300 characters")
    if type(limit) is not int or not 1 <= limit <= 5:
        raise ValueError("Limit must be 1–5")
    query = query.casefold().replace("’", "'").replace("‘", "'").replace("ʻ", "'").replace("ʼ", "'")
    terms = list(dict.fromkeys(word for word in WORD.findall(query) if len(word) > 2))[:12]
    stems = {stem(term) for term in terms}
    for alias, synonyms in ALIASES.items():
        if alias in terms or alias in stems or ("'" in alias and alias in query):
            terms.extend(word for word in synonyms if word not in terms)
    if not terms:
        return {"status": "no_match", "sources": []}

    database.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database, timeout=3)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        docs = approved_snapshot(root.resolve())
        db.execute("CREATE TABLE IF NOT EXISTS files (source TEXT PRIMARY KEY, digest TEXT)")
        db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(source UNINDEXED, "
                   "heading, first_line UNINDEXED, last_line UNINDEXED, body)")
        db.execute("CREATE TABLE IF NOT EXISTS index_meta (key TEXT PRIMARY KEY, value INTEGER)")
        version = db.execute("SELECT value FROM index_meta WHERE key='chunker_version'").fetchone()
        if version != (INDEX_VERSION,):
            # Cached source hashes alone cannot detect a repaired extraction algorithm.
            db.execute("DELETE FROM chunks")
            db.execute("DELETE FROM files")
            db.execute("INSERT OR REPLACE INTO index_meta VALUES ('chunker_version', ?)", (INDEX_VERSION,))
        old = dict(db.execute("SELECT source, digest FROM files"))
        for name in old:
            if name not in docs or old[name] != docs[name][0]:
                db.execute("DELETE FROM chunks WHERE source = ?", (name,))
                db.execute("DELETE FROM files WHERE source = ?", (name,))
        for name, (digest, body, first_line) in docs.items():
            if old.get(name) == digest:
                continue
            db.execute("INSERT INTO files VALUES (?, ?)", (name, digest))
            db.executemany("INSERT INTO chunks VALUES (?, ?, ?, ?, ?)",
                           ((name, *section) for section in sections(body, first_line)))
        # Terms come from WORD (letters/digits only), so quoting keeps FTS operators inert.
        expression = " OR ".join(f'"{stem(term)}"*' for term in terms)
        rows = db.execute(
            "SELECT source, heading, first_line, last_line, body FROM chunks "
            "WHERE chunks MATCH ? ORDER BY bm25(chunks, 0, 3, 0, 0, 1), source, first_line LIMIT ?",
            (expression, limit),
        ).fetchall()
    return {
        "status": "matched" if rows else "no_match",
        "sources": [
            {"file": f"knowledge/{source}", "heading": heading,
             "lines": [first, last], "excerpt": excerpt}
            for source, heading, first, last, excerpt in rows
        ],
    }
