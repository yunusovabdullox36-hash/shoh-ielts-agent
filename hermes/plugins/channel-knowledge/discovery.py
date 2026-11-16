"""Bounded installed-only workflow discovery; expose ties instead of guessing."""

from pathlib import Path
import re
import unicodedata


CATALOG = (
    ("ieltsshokh-html", "Build Writing and Reading HTML", "writing reading html insho oqish diagram essay cdi"),
    ("ielts-material-package", "Coordinate source files, answers and deliverables", "package paket savollar pdf mock listening speaking grammar vocabulary lugat javoblar material"),
    ("ielts-marketing", "Draft campaigns, copy and experiments", "marketing reklama kampaniya campaign sotuv social content kontent promo reklamalar"),
    ("ielts-people", "Draft hiring rubrics, interviews and onboarding", "hr hiring hire people intervyu xodim ishchi yollash jamoa ishga onboarding recruitment teacher vacancy vakansiya"),
    ("ielts-media", "Plan images, audio scripts and video edits", "media image rasm video montaj reel reels storyboard generate edit audio ovoz podkast podcast surat"),
    ("channel-analysis", "Analyze supplied posts and metrics", "kanal channel analytics tahlil metrika views auditoriya statistika qamrov engagement"),
    ("memory-management", "Prepare or save verified preferences using available tools", "memory xotira eslab esla remember saqla"),
    ("channel-decision-tree", "Route sources, drafts and approval requirements", "routing route workflow yonaltirish tasdiq nashr publish publication"),
    ("find-skills", "Find a suitable installed workflow", "skill skills konikma qobiliyat"),
    ("ielts-rag-governance", "Check evidence and knowledge-source authority", "rag retrieval knowledge bilim manba dalil embedding chunking obsidian"),
    ("ielts-design-quality", "Review brand and visual quality", "design dizayn brand brend logo ui ux accessibility rang tipografiya"),
    ("client-integration-boundaries", "Scope client-owned account access", "integration integratsiya oauth account akkaunt credential ulanish mcp"),
    ("client-automation-blueprints", "Plan client automation with approval gates", "automation avtomatlashtirish avtomatizatsiya n8n composio webhook zapier"),
    ("hermes-agent", "Inspect Hermes operations within available permissions", "hermes gateway configuration konfiguratsiya sozlama"),
    ("shoh-onboarding", "Run first-run setup and integrations", "onboarding setup sozla sozlash tanishuv integratsiya obsidian google gmail calendar drive model claude"),
    ("shoh-self-care", "Recover from stuck work and handle updates", "update yangila yangilash yangilanish tiqildi qotib xato ishlamayapti tikla restart"),
)
SKILLS_ROOT = Path(__file__).resolve().parents[2] / "skills"
SUFFIXES = ("laringizni", "larimizni", "larni", "larini", "ingizni", "lardan", "larga", "lar", "ning", "ni", "ga", "dan", "da", "im")


def normalize(text):
    value = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"['‘’ʻʼ`]+", "", value)


def installed_names(root):
    """Read only bounded frontmatter, including nested skill directories."""
    root = Path(root).resolve()
    names = set()
    for path in root.rglob("SKILL.md"):
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            continue
        try:
            with path.open(encoding="utf-8-sig") as handle:
                header = handle.read(8192)
        except (OSError, UnicodeError):
            continue
        if not header.startswith("---\n"):
            continue
        frontmatter = header.split("\n---", 1)[0]
        match = re.search(r"(?m)^name:\s*[\"']?([a-z0-9-]+)[\"']?\s*$", frontmatter)
        if match:
            names.add(match[1])
    return names


def find(query, *, skills_root=None):
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 300:
        return {"status": "invalid_query", "skills": [], "ambiguous": False}
    normalized = normalize(query)
    terms = set(re.findall(r"[^\W_]+", normalized))
    vocabulary = {word for _, _, tags in CATALOG for word in tags.split()}
    # Only stem to known routing vocabulary; avoid unrestricted substring hits.
    expanded = terms | {term[:-len(suffix)] for term in terms for suffix in SUFFIXES
                        if term.endswith(suffix) and term[:-len(suffix)] in vocabulary}
    available = installed_names(skills_root if skills_root is not None else SKILLS_ROOT)
    ranked = []
    for name, output, tags in CATALOG:
        if name not in available:
            continue
        score = len(expanded & set(tags.split()))
        if re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", normalized):
            score += 20
        if score:
            ranked.append((score, name, output))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    matches = [{"name": name, "output": output, "matched_terms": score}
               for score, name, output in ranked[:3]]
    return {"status": "matched" if matches else "no_match", "skills": matches,
            "ambiguous": len(ranked) > 1 and ranked[0][0] == ranked[1][0],
            "external_catalog": "https://hermes-agent.nousresearch.com/docs/user-guide/features/skills"}
