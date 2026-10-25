"""Main-text extraction using only the standard library html.parser.

This is a conservative general extractor, not a reader-mode implementation:
it captures visible text and the title tag, skips script, style, noscript,
svg, and template content, and imposes hard size caps. Complex layouts (pay
walls, infinite scroll shells, heavy JS rendering) may yield little text;
callers must treat empty extraction as "no extractable text", never as a
reason to invent content.
"""

from __future__ import annotations

import json
from html.parser import HTMLParser

from arguo.retrieval.fetcher import FetchResult
from arguo.utilities.text import normalize_whitespace

_MAX_TEXT_CHARS = 20_000
_MIN_CHUNK_CHARS = 25

_SKIP_TAGS = frozenset({"script", "style", "noscript", "svg", "template"})
_TITLE_TAG = "title"
_BLOCK_TAGS = frozenset(
    {
        "address", "article", "aside", "blockquote", "br", "dd", "div", "dl",
        "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1",
        "h2", "h3", "h4", "h5", "h6", "header", "hr", "li", "main", "nav",
        "ol", "p", "pre", "section", "table", "tbody", "td", "tfoot", "th",
        "thead", "tr", "ul",
    }
)


class _TextExtractor(HTMLParser):
    """Collect title text and visible body text, skipping ignored elements."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_stack: list[str] = []
        self._in_title = False
        self._title_parts: list[str] = []
        self._buffer: list[str] = []
        self._chunks: list[str] = []

    def flush(self) -> None:
        """Close the current text chunk, dropping chunks under 25 characters."""
        if not self._buffer:
            return
        chunk = normalize_whitespace("".join(self._buffer))
        self._buffer.clear()
        if len(chunk) >= _MIN_CHUNK_CHARS:
            self._chunks.append(chunk)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP_TAGS:
            self.flush()
            self._skip_stack.append(tag)
            return
        if tag == _TITLE_TAG:
            self._in_title = True
            return
        if tag in _BLOCK_TAGS:
            self.flush()

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS:
            if self._skip_stack and tag in self._skip_stack:
                # Pop until the matching open tag so malformed nesting cannot
                # leave the extractor permanently muted.
                while self._skip_stack:
                    if self._skip_stack.pop() == tag:
                        break
            return
        if tag == _TITLE_TAG:
            self._in_title = False
            return
        if tag in _BLOCK_TAGS:
            self.flush()

    def handle_data(self, data: str) -> None:
        if self._skip_stack:
            return
        if self._in_title:
            self._title_parts.append(data)
            return
        self._buffer.append(data)

    def close(self) -> None:
        super().close()
        self.flush()

    @property
    def title(self) -> str | None:
        title = normalize_whitespace("".join(self._title_parts))
        return title or None

    @property
    def text(self) -> str | None:
        text = normalize_whitespace(" ".join(self._chunks))
        if not text:
            return None
        return text[:_MAX_TEXT_CHARS]


def extract_main_text(html: str) -> tuple[str | None, str | None]:
    """Return (title, main text) for an HTML document, either may be None.

    Text chunks shorter than 25 characters are dropped to skip navigation
    fragments, output whitespace is collapsed, and the result is capped at
    roughly 20k characters.
    """
    if not isinstance(html, str) or not html:
        return None, None
    parser = _TextExtractor()
    parser.feed(html)
    parser.close()
    return parser.title, parser.text


def _collect_json_strings(node: object, out: list[str]) -> None:
    """Recursively collect string values of length >= 25 from a JSON value."""
    if isinstance(node, str):
        cleaned = normalize_whitespace(node)
        if len(cleaned) >= _MIN_CHUNK_CHARS:
            out.append(cleaned)
    elif isinstance(node, dict):
        for value in node.values():
            _collect_json_strings(value, out)
    elif isinstance(node, list):
        for value in node:
            _collect_json_strings(value, out)


def extract_from_fetch(result: FetchResult) -> tuple[str | None, str | None]:
    """Route a FetchResult to the right extraction path.

    HTML and XHTML go through extract_main_text; JSON is reduced to its text
    fields (string values, joined); plain text passes through; PDFs were
    never parsed so they yield (None, None). Failed fetches also yield
    (None, None).
    """
    if result.error or not result.page_text:
        return None, None
    content_type = (result.content_type or "").lower()
    if "pdf" in content_type:
        return None, None
    if "html" in content_type or "xhtml" in content_type or "xml" in content_type:
        return extract_main_text(result.page_text)
    if "json" in content_type:
        try:
            data = json.loads(result.page_text)
        except ValueError:
            return None, normalize_whitespace(result.page_text)[:_MAX_TEXT_CHARS] or None
        parts: list[str] = []
        _collect_json_strings(data, parts)
        text = normalize_whitespace("\n".join(parts))[:_MAX_TEXT_CHARS] or None
        title = None
        if isinstance(data, dict) and isinstance(data.get("title"), str):
            title = normalize_whitespace(data["title"]) or None
        return title, text
    # text/plain and anything unrecognised but allowed: pass through, capped.
    return None, result.page_text[:_MAX_TEXT_CHARS] or None
