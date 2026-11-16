"""Build and lint HTML inside this profile's generated media cache."""

from base64 import b64encode
from copy import deepcopy
from hashlib import sha256
import importlib.util
import importlib
from pathlib import Path
import sys
import tempfile
from uuid import uuid4


def load_bundle(skill: Path):
    # A gateway may host multiple profiles. Never reuse another profile's
    # renderers or keep the old code after a bundle revision is deployed.
    scripts = skill.resolve(strict=True) / "scripts"
    digest = sha256(str(scripts).encode("utf-8"))
    for source in sorted(scripts.glob("*.py")):
        digest.update(source.name.encode("utf-8"))
        digest.update(source.read_bytes())
    package_name = "_channel_ieltsshokh_renderers_" + digest.hexdigest()[:24]
    if package_name not in sys.modules:
        location = scripts / "__init__.py"
        spec = importlib.util.spec_from_file_location(package_name, location)
        module = importlib.util.module_from_spec(spec)
        sys.modules[package_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(package_name, None)
            raise
    lint = importlib.import_module(package_name + ".lint")
    material = importlib.import_module(package_name + ".material")

    return lint.lint, material.render


def source_image(path, cache: Path, document_cache: Path | None = None):
    if not isinstance(path, str) or not Path(path).is_absolute():
        raise ValueError("Use the exact cached source image path")
    file = Path(path).resolve(strict=True)
    is_photo = file.parent == cache.resolve() and file.name.startswith("img_")
    is_document = (document_cache is not None and file.parent == document_cache.resolve()
                   and file.name.startswith("doc_"))
    if not (is_photo or is_document) or not file.is_file():
        raise ValueError("Choose an original image from this profile's Telegram image cache")
    with file.open("rb") as stream:
        raw = stream.read(10 * 1024 * 1024 + 1)
    if not 0 < len(raw) <= 10 * 1024 * 1024:
        raise ValueError("Source image must be at most 10 MiB")
    if raw.startswith(b"\x89PNG\r\n\x1a\n") and file.suffix.lower() == ".png":
        mime = "png"
    elif raw.startswith(b"\xff\xd8\xff") and file.suffix.lower() in {".jpg", ".jpeg"}:
        mime = "jpeg"
    elif raw[:4] == b"RIFF" and raw[8:12] == b"WEBP" and file.suffix.lower() == ".webp":
        mime = "webp"
    else:
        raise ValueError("Source image must be a PNG, JPEG or WebP")
    return (f"data:image/{mime};base64," + b64encode(raw).decode("ascii"),
            {"mode": "original", "sha256": sha256(raw).hexdigest(), "bytes": len(raw)})


def build(root: Path, skill: Path, kind: str, data, *, image_cache=None, document_cache=None,
          practice_visual=False):
    lint, render = load_bundle(skill)
    build_id = uuid4().hex
    images = {}
    evidence = None
    if kind == "writing" and isinstance(data, dict):
        data = deepcopy(data)
        tasks = data.get("tasks")
        if isinstance(tasks, list):
            for n, task in enumerate(tasks, 1):
                if not isinstance(task, dict):
                    continue
                path = task.pop("source_image_path", None)
                if path is not None:
                    if n != 1 or image_cache is None:
                        raise ValueError("Source image is supported for Writing Task 1 in the Shoh profile")
                    if task.get("chart_svg"):
                        raise ValueError("Use the original image alone when a source exists")
                    images[n], evidence = source_image(path, image_cache, document_cache)
                if image_cache is not None and task.get("chart_svg") and not practice_visual:
                    raise ValueError("Use the original Task 1 image. SVG is reserved for newly invented practice data.")
                if n == 1 and image_cache is not None and not (path or task.get("chart_svg")):
                    raise ValueError("Writing Task 1 needs its original image or an explicitly new practice chart")
    body = render(kind, data, build_id, source_images=images)
    root.mkdir(parents=True, exist_ok=True)
    destination = root / f"IELTSSHOKH-{kind}-{build_id[:12]}.html"
    with tempfile.NamedTemporaryFile(dir=root, suffix=".html", delete=False) as stream:
        staging = Path(stream.name)
    try:
        staging.write_text(body, encoding="utf-8", newline="\n")
        issues = lint(staging)
        if issues:
            return {"status": "lint_failed", "issues": issues[:10]}
        staging.replace(destination)
    finally:
        staging.unlink(missing_ok=True)
    result = {"status": "ok", "lint": "passed", "file": destination.name,
              "media": f"MEDIA:{destination.as_posix()}", "bytes": destination.stat().st_size}
    if evidence:
        result["source_visual"] = evidence
    return result
