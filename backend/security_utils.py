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
