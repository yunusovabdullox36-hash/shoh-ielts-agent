"""Read only this profile's cached documents and summarize HTML without running it."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
from xml.etree.ElementTree import ParseError

MAX_BYTES = 20 * 1024 * 1024
OFFICE_TEXT = {".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp", ".epub"}


class HtmlText(HTMLParser):
    hidden_tags = {"script", "style", "template"}
    block_tags = {"article", "div", "section", "p", "li", "br", "h1", "h2", "h3", "tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = None
        self.text = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        if self.hidden:
            return
        if tag in self.hidden_tags:
            self.hidden = tag
        elif tag in self.block_tags:
            self.text.append("\n")
        elif tag in {"img", "svg"} and len(self.images) < 20:
            values = dict(attrs)
            source = values.get("src") or ""
            self.images.append({
                "type": tag,
                "label": (values.get("alt") or values.get("aria-label") or "")[:300],
                "embedded": tag == "svg" or source.startswith("data:"),
            })

    def handle_endtag(self, tag):
        if tag == self.hidden:
            self.hidden = None
        elif not self.hidden and tag in self.block_tags:
            self.text.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.text.append(data)


def inspect(root: Path, path: str, offset: int, limit: int, mode: str):
    if (not isinstance(path, str) or type(offset) is not int or offset < 0
            or type(limit) is not int or not 1 <= limit <= 12000
            or mode not in {"text", "source"}):
        raise ValueError("Invalid path or page")
    supplied = Path(path)
    if not supplied.is_absolute():
        raise PermissionError("Use an attachment's absolute cached path")
    source = supplied.resolve(strict=True)
    if (source.parent != root.resolve() or not source.name.startswith("doc_")
            or not source.is_file()):
        raise PermissionError("Only cached attachments for this profile are readable")
    with source.open("rb") as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        return {"status": "too_large", "limit_bytes": MAX_BYTES}
    suffix = source.suffix.lower()
    try:
        encoding = ("utf-32" if data.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")) else
                    "utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
        content = data.decode(encoding)
    except UnicodeError:
        content = None
    if content is None and suffix in {".html", ".htm", ".txt", ".csv", ".md"}:
        try:
            content = data.decode("cp1252")
        except UnicodeError:
            pass
    if (content is None or "\x00" in content or data.startswith((b"%PDF-", b"PK\x03\x04"))
            or (suffix == ".exe" and data.startswith(b"MZ"))):
        content = None
        if mode == "text":
            try:
                content = extract_binary(source, suffix)
            except ImportError:
                return {"status": "extraction_unavailable", "suffix": suffix}
            except (OSError, ValueError, zipfile.BadZipFile, subprocess.SubprocessError, ParseError):
                return {"status": "extraction_failed", "suffix": suffix}
        if not content or not content.strip():
            return {"status": "binary_or_unsupported", "suffix": suffix, "bytes": len(data)}
    images = []
    html_data = []
    if source.suffix.lower() in {".html", ".htm"} and mode == "text":
        parser = HtmlText()
        parser.feed(content)
        for match in re.finditer(r"\bconst\s+(TEST|KIT|ANS|KW|FB)\s*=\s*(?=\{)", content):
            name = match[1]
            if name in html_data:
                continue
            try:
                value, _ = json.JSONDecoder().raw_decode(content, match.end())
            except (ValueError, RecursionError):
                continue
            html_data.append(name)
            parser.text.extend(["\n", f"[Structured HTML data: {name}]", "\n",
                                json.dumps(value, ensure_ascii=False, indent=2), "\n"])
        content = "\n".join(line for line in
                            (re.sub(r"\s+", " ", line).strip() for line in "".join(parser.text).splitlines())
                            if line)
        images = parser.images
    end = offset + limit
    return {"status": "ok", "text": content[offset:end], "images": images, "html_data": html_data,
            "next_offset": end if end < len(content) else None, "total_characters": len(content)}


def extract_binary(source: Path, suffix: str):
    if suffix == ".pdf":
        executable = shutil.which("pdftotext")
        if not executable:
            # The native Windows Hermes Git bundle ships Poppler beside git.exe.
            git = shutil.which("git")
            candidates = ([Path(git).parents[1] / "mingw64" / "bin" / "pdftotext.exe"] if git else [])
            if len(source.parents) > 4:
                candidates += sorted(source.parents[4].glob("tools/git-*/mingw64/bin/pdftotext.exe"))
            executable = next((str(p) for p in candidates if p.is_file()), None)
        if executable:
            return subprocess.run([executable, "-enc", "UTF-8", "-f", "1", "-l", "100", str(source), "-"],
                                  capture_output=True, check=True, timeout=12,
                                  creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.decode("utf-8")
    if suffix in OFFICE_TEXT:
        with zipfile.ZipFile(source) as archive:
            entries = archive.infolist()
            if len(entries) > 2000 or sum(entry.file_size for entry in entries) > 40 * 1024 * 1024:
                raise ValueError("Expanded archive exceeds document limit")
            if suffix not in {".docx", ".xlsx"}:
                from xml.etree import ElementTree as ET

                pages = []
                for name in sorted(archive.namelist(), key=lambda n: (len(n), n)):
                    if name == "content.xml" or re.fullmatch(r"ppt/slides/slide\d+\.xml", name):
                        doc = ET.fromstring(archive.read(name))
                        if suffix == ".pptx":
                            chunks = (n.text for n in doc.iter() if n.tag.endswith("}t") and n.text)
                        else:
                            chunks = ("".join(n.itertext()) for n in doc.iter() if n.tag.endswith(("}p", "}h")))
                        pages.append("\n".join(chunks))
                    elif suffix == ".epub" and Path(name).suffix.lower() in {".html", ".xhtml"}:
                        parser = HtmlText()
                        parser.feed(archive.read(name).decode("utf-8-sig"))
                        pages.append("".join(parser.text))
                return "\n\n".join(pages)
        from tools.read_extract import ExtractionError, extract_document_text

        try:
            return extract_document_text(str(source))
        except ExtractionError as exc:
            raise ValueError("Unsupported or damaged Office document") from exc
    return None
