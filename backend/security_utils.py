from typing import Optional

import bleach


ALLOWED_HTML_TAGS = [
    "p", "br", "div", "span", "strong", "em", "u", "s",
    "ul", "ol", "li", "blockquote", "pre", "code",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "a", "img",
]

ALLOWED_HTML_ATTRIBUTES = {
    "*": ["class"],
    "a": ["href", "target", "rel"],
    "img": ["src", "alt", "title"],
}

ALLOWED_HTML_PROTOCOLS = ["http", "https", "mailto"]


def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "", 1).strip()
    return token or None


def sanitize_html(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = bleach.clean(
        value,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        protocols=ALLOWED_HTML_PROTOCOLS,
        strip=True,
    )
    return bleach.linkify(cleaned)


def sanitize_plaintext(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return bleach.clean(value, tags=[], attributes={}, strip=True).strip()


def get_git_commit() -> Optional[str]:
    import os
    import subprocess
    commit = os.getenv("RENDER_GIT_COMMIT")
    if commit and commit.strip():
        return commit.strip()
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=base_dir).decode("utf-8").strip()
    except Exception:
        return None


def get_git_branch() -> Optional[str]:
    import os
    import subprocess
    branch = os.getenv("RENDER_GIT_BRANCH")
    if branch and branch.strip():
        return branch.strip()
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return subprocess.check_output(["git", "branch", "--show-current"], cwd=base_dir).decode("utf-8").strip()
    except Exception:
        return None
