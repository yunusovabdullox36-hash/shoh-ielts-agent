"""Translate scoped JSON content into the original CDI renderers' data."""

import html
import json
import re
from types import SimpleNamespace
from xml.etree import ElementTree as ET

from . import build_reading, build_writing


def string(value, limit=8000, *, empty=False):
    if (not isinstance(value, str) or len(value) > limit
            or (not empty and not value.strip()) or "\x00" in value):
        raise ValueError("Expected text within the field limit")
    value.encode("utf-8")
    return value


def esc(value, limit=8000, *, empty=False):
    return html.escape(string(value, limit, empty=empty))


def items(value, maximum, *, minimum=1):
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ValueError("Unexpected number of items")
    return value


def fields(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= value.keys() <= set(required) | set(optional):
        raise ValueError("Expected object fields: " + ", ".join(required))
    return value


def number(value, low=1, high=40):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("Number outside the allowed range")
    return value


def pair(row):
    return items(row, 2, minimum=2)


def chart_svg(source):
    if source is None:
        return ""
    source = string(source, 60000)
    if "<!" in source or "<?" in source:
        raise ValueError("SVG declarations are not allowed")
    root = ET.fromstring(source)
    tags = {"svg", "g", "rect", "line", "circle", "ellipse", "path", "polyline", "polygon",
            "text", "tspan", "title", "desc"}
    attrs = {"viewBox", "width", "height", "x", "y", "x1", "y1", "x2", "y2", "cx", "cy",
             "r", "rx", "ry", "d", "points", "fill", "stroke", "stroke-width", "opacity",
             "stroke-dasharray", "stroke-linecap", "stroke-linejoin", "text-anchor",
             "dominant-baseline", "font-size", "font-family", "font-weight", "transform",
             "role", "aria-label"}
    svg_ns = "{http://www.w3.org/2000/svg}"
    if root.tag not in {"svg", svg_ns + "svg"} or "viewBox" not in root.attrib:
        raise ValueError("Chart requires an SVG root and viewBox")
    for index, node in enumerate(root.iter()):
        node.tag = node.tag.removeprefix(svg_ns)
        if index >= 600 or node.tag not in tags or node.attrib.keys() - attrs:
            raise ValueError("SVG must contain static shapes and text only")
        for key, value in node.attrib.items():
            if len(value) > 8000 or (key in {"fill", "stroke"} and
                    not re.fullmatch(r"#[0-9a-fA-F]{3,8}|[a-zA-Z]+|rgba?\([\d.,% ]+\)", value)):
                raise ValueError("Unsupported SVG attribute value")
    return ET.tostring(root, encoding="unicode")


def writing(data, build_id, source_images=None):
    fields(data, ("title", "tasks"))
    title = string(data["title"], 100)
    tasks, kit = {}, {}
    for n, task in enumerate(items(data["tasks"], 2, minimum=2), start=1):
        fields(task, ("prompt", "model", "vocabulary", "toolkit"), ("chart_svg", "instruction"))
        prompt = string(task["prompt"], 4000)
        minimum = 150 if n == 1 else 250
        tasks[n] = {
            "title": f"Writing Task {n}",
            "inst": esc(task.get("instruction", f"You should spend about {20 * n} minutes on this task. Write at least {minimum} words."), 500),
            "min": minimum,
            "question": prompt,
            "prompt_html": "".join(f"<p>{esc(line)}</p>" for line in prompt.splitlines() if line.strip()),
            "chart_svg": chart_svg(task.get("chart_svg")),
            "source_image": (source_images or {}).get(n),
            "model": "".join(f"<p>{esc(line)}</p>" for line in items(task["model"], 12)),
            "vocab": [[string(term, 150), string(note, 500)]
                      for term, note in map(pair, items(task["vocabulary"], 20))],
        }
        kit[n] = [[esc(label, 100), [[string(phrase, 250), esc(hint, 400, empty=True)]
                                    for phrase, hint in map(pair, items(group, 20))]]
                  for label, group in map(pair, items(task["toolkit"], 8))]
    return build_writing.build(SimpleNamespace(ID=build_id, LABEL=title, LABEL_HTML=esc(title, 100),
                                               TASKS=tasks, KIT=kit))


def choices(value):
    opts = [[letter(code), esc(label, 500)] for code, label in map(pair, items(value, 15, minimum=2))]
    if len({code for code, _ in opts}) != len(opts):
        raise ValueError("Duplicate choice letter")
    return opts


def letter(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Z]", value):
        raise ValueError("Expected a single uppercase choice letter")
    return value


def section(value):
    if not isinstance(value, dict):
        raise ValueError("Expected question section")
    kind = value.get("type")
    extra = {"tfng": ("qs",), "ynng": ("qs",), "notes": ("text",), "mc": ("qs", "options"),
             "chip": ("qs", "letters"), "multi": ("q", "options", "stem")}
    if not isinstance(kind, str) or kind not in extra:
        raise ValueError("Unsupported question section")
    fields(value, ("type", "label", "desc") + extra[kind],
           {"notes": ("title",), "chip": ("box",), "multi": ("n",)}.get(kind, ()))
    s = {"type": kind, "label": esc(value["label"], 150), "desc": esc(value["desc"], 1500)}
    if kind == "notes":
        s["title"] = esc(value.get("title", ""), 150, empty=True)
        s["html"] = esc(value["text"], 8000).replace("\n", "<br>")
        qs = [number(int(q)) for q in re.findall(r"\[\[([0-9]{1,2})\]\]", s["html"])]
    elif kind == "multi":
        s.update(q=number(value["q"]), n=number(value.get("n", 2), 2, 5),
                 stem=esc(value["stem"], 800), options=choices(value["options"]))
        qs = list(range(s["q"], s["q"] + s["n"]))
    else:
        qs = s["qs"] = [number(q) for q in items(value["qs"], 40)]
        if kind == "chip":
            s["letters"] = [letter(code) for code in items(value["letters"], 15, minimum=2)]
            s["box"] = esc(value.get("box", ""), 2500, empty=True).replace("\n", "<br>")
        if kind == "mc":
            fields(value["options"], tuple(str(q) for q in qs))
            s["options"] = {q: choices(value["options"][str(q)]) for q in qs}
    if not qs or len(set(qs)) != len(qs) or max(qs) > 40:
        raise ValueError("Invalid or repeated question numbers")
    return s, qs


def reading(data):
    fields(data, ("title", "passages", "questions"), ("minutes",))
    passages, numbers, evidence, answer_rules = [], [], {}, {}
    for passage in items(data["passages"], 3):
        fields(passage, ("num", "title", "caption", "paragraphs", "sections"))
        paragraphs = [string(p) for p in items(passage["paragraphs"], 50)]
        secs, qs = zip(*(section(s) for s in items(passage["sections"], 15)))
        seq = [q for group in qs for q in group]
        if sorted(seq) != list(range(min(seq), max(seq) + 1)):
            raise ValueError("Passage question numbering must be consecutive and unique")
        for s, group in zip(secs, qs):
            for q in group:
                kind = s["type"]
                allowed = {"tfng": ["TRUE", "FALSE", "NOT GIVEN"], "ynng": ["YES", "NO", "NOT GIVEN"],
                           "chip": s.get("letters"), "multi": [code for code, _ in s.get("options", [])]
                           if kind == "multi" else None}.get(kind)
                if kind == "mc":
                    allowed = [code for code, _ in s["options"][q]]
                answer_rules[q] = allowed
        for paragraph in paragraphs:
            for q, quote in re.findall(r"\{\{([0-9]{1,2})\|([^{}]+)\}\}", paragraph):
                if int(q) not in seq:
                    raise ValueError("Evidence marker belongs to another passage")
                evidence.setdefault(int(q), []).append(quote)
        passages.append({"num": number(passage["num"], 1, 3), "title": esc(passage["title"], 200),
                         "caption": esc(passage["caption"], 500), "paras": [esc(p) for p in paragraphs],
                         "sections": list(secs)})
        numbers.extend(sorted(seq))
    if (numbers != list(range(numbers[0], numbers[-1] + 1))
            or len({p["num"] for p in passages}) != len(passages)):
        raise ValueError("Passages must have distinct numbers and consecutive questions")
    fields(data["questions"], tuple(str(q) for q in numbers))
    qt, an, accepted = {}, {}, {}
    for q in numbers:
        entry = fields(data["questions"][str(q)], ("prompt", "answer", "keyword", "paraphrase", "evidence", "explanation"), ("accept",))
        answer = string(entry["answer"], 100)
        if not re.fullmatch(r"[\w .'’\-]+", answer) or (answer_rules[q] is not None and answer not in answer_rules[q]):
            raise ValueError(f"Q{q} answer does not match the question type")
        quote = string(entry["evidence"], 1500)
        if quote not in evidence.get(q, []):
            raise ValueError(f"Q{q} evidence must match an exact passage marker")
        qt[q] = esc(entry["prompt"], 1000)
        an[q] = [answer, esc(entry["keyword"], 400), esc(entry["paraphrase"], 800),
                 esc(quote, 1500), esc(entry["explanation"], 2500)]
        if "accept" in entry:
            if answer_rules[q] is not None:
                raise ValueError("Answer variants are only allowed for text answers")
            accepted[q] = [answer, *[string(v, 100) for v in items(entry["accept"], 8)]]
    for p in passages:
        for s in p["sections"]:
            if s["type"] == "multi" and len({an[q][0] for q in range(s["q"], s["q"] + s["n"])}) != s["n"]:
                raise ValueError("Multiple choice answers must be distinct")
    minutes = number(data.get("minutes", 20 * len(passages)), 1, 60)
    return build_reading.build(SimpleNamespace(TITLE=esc(data["title"], 100), PASSAGES=passages,
                                               QT=qt, AN=an, ACCEPT=accepted, MINUTES=minutes))


def render(kind, data, build_id, *, source_images=None):
    if len(json.dumps(data, ensure_ascii=False)) > 160000:
        raise ValueError("Material exceeds the input limit")
    if kind == "writing":
        return writing(data, build_id, source_images)
    if kind == "reading":
        return reading(data)
    raise ValueError("Choose writing or reading")
