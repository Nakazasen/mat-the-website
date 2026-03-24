from backend.security_utils import extract_bearer_token, sanitize_html, sanitize_plaintext


def test_extract_bearer_token_accepts_valid_header():
    assert extract_bearer_token("Bearer abc.def.ghi") == "abc.def.ghi"


def test_extract_bearer_token_rejects_invalid_header():
    assert extract_bearer_token(None) is None
    assert extract_bearer_token("") is None
    assert extract_bearer_token("Token abc") is None
    assert extract_bearer_token("Bearer   ") is None


def test_sanitize_html_removes_script_and_event_handlers():
    dirty = '<p onclick="alert(1)">safe</p><script>alert(1)</script><img src="x" onerror="alert(2)">'
    cleaned = sanitize_html(dirty)
    assert "<script" not in cleaned
    assert "onclick" not in cleaned
    assert "onerror" not in cleaned
    assert "<p>safe</p>" in cleaned


def test_sanitize_plaintext_strips_tags():
    dirty = "<b>Hello</b> <script>alert(1)</script>World"
    assert sanitize_plaintext(dirty) == "Hello alert(1)World"
