"""Pure sanitizer: keep Cyrillic/Latin/code, strip foreign-script leaks."""

from __future__ import annotations

import re
import unicodedata

# Letters in these ranges stay. Everything else with Unicode category L* is removed.
_KEEP_LETTER_RANGES: tuple[tuple[int, int], ...] = (
    (0x0000, 0x024F),  # Basic Latin, Latin-1, Extended-A/B
    (0x0250, 0x02FF),  # IPA + spacing modifier letters
    (0x0370, 0x03FF),  # Greek and Coptic (math: π, α, Σ)
    (0x0400, 0x04FF),  # Cyrillic
    (0x0500, 0x052F),  # Cyrillic Supplement
    (0x1C80, 0x1C8F),  # Cyrillic Extended-C
    (0x1D00, 0x1DBF),  # Phonetic Extensions
    (0x1E00, 0x1EFF),  # Latin Extended Additional
    (0x1F00, 0x1FFF),  # Greek Extended
    (0x2100, 0x214F),  # Letterlike Symbols (ℝ)
    (0x2C60, 0x2C7F),  # Latin Extended-C
    (0x2DE0, 0x2DFF),  # Cyrillic Extended-A
    (0xA640, 0xA69F),  # Cyrillic Extended-B
    (0xA720, 0xA7FF),  # Latin Extended-D
    (0xAB30, 0xAB6F),  # Latin Extended-E
    (0xFB00, 0xFB06),  # Latin ligatures
    (0x10780, 0x107BF),  # Latin Extended-F
    (0x1D400, 0x1D7FF),  # Mathematical Alphanumeric Symbols
    (0x1DF00, 0x1DFFF),  # Latin Extended-G
)

# Not always letters; leftover after CJK ideographs would look like junk.
_CJK_PUNCT_RANGES: tuple[tuple[int, int], ...] = (
    (0x2E80, 0x2EFF),  # CJK Radicals Supplement
    (0x2F00, 0x2FDF),  # Kangxi Radicals
    (0x2FF0, 0x2FFF),  # Ideographic Description Characters
    (0x3000, 0x303F),  # CJK Symbols and Punctuation
    (0x31C0, 0x31EF),  # CJK Strokes
    (0x3200, 0x32FF),  # Enclosed CJK Letters and Months
    (0x3300, 0x33FF),  # CJK Compatibility
    (0xFE30, 0xFE4F),  # CJK Compatibility Forms
)

# Do not use MULTILINE: `$` would close the fence at the end of the info line.
_FENCE_RE = re.compile(r"```[\s\S]*?(?:```|\Z)")
_INLINE_RE = re.compile(r"`[^`]*`")
_MULTI_SPACE_RE = re.compile(r" {2,}")
_MULTI_NL_RE = re.compile(r"\n{3,}")


def _in_ranges(codepoint: int, ranges: tuple[tuple[int, int], ...]) -> bool:
    return any(start <= codepoint <= end for start, end in ranges)


def unwrap_fullwidth(text: str) -> str:
    """Map fullwidth ASCII (U+FF01–FF5E) to regular ASCII. No global NFKC."""
    out: list[str] = []
    for char in text:
        code = ord(char)
        if 0xFF01 <= code <= 0xFF5E:
            out.append(chr(code - 0xFEE0))
        else:
            out.append(char)
    return "".join(out)


def should_strip(char: str) -> bool:
    code = ord(char)
    if _in_ranges(code, _CJK_PUNCT_RANGES):
        return True
    if unicodedata.category(char).startswith("L") and not _in_ranges(
        code, _KEEP_LETTER_RANGES
    ):
        return True
    return False


def contains_foreign(text: str) -> bool:
    """True if any character would be stripped (same predicate as output)."""
    if not text:
        return False
    return any(should_strip(char) for char in unwrap_fullwidth(text))


def _split_inline(text: str) -> list[tuple[str, str]]:
    parts: list[tuple[str, str]] = []
    last = 0
    for match in _INLINE_RE.finditer(text):
        if match.start() > last:
            parts.append(("text", text[last : match.start()]))
        parts.append(("code", match.group(0)))
        last = match.end()
    if last < len(text):
        parts.append(("text", text[last:]))
    return parts or [("text", text)]


def split_markdown_code(text: str) -> list[tuple[str, str]]:
    """Split into ('text'|'code', chunk). Fences first, then inline backticks."""
    parts: list[tuple[str, str]] = []
    last = 0
    for match in _FENCE_RE.finditer(text):
        if match.start() > last:
            parts.extend(_split_inline(text[last : match.start()]))
        parts.append(("code", match.group(0)))
        last = match.end()
    if last < len(text):
        parts.extend(_split_inline(text[last:]))
    return parts or [("text", text)]


def collapse_ws(text: str) -> str:
    text = _MULTI_SPACE_RE.sub(" ", text)
    return _MULTI_NL_RE.sub("\n\n", text)


def _clean_prose(text: str) -> str:
    unwrapped = unwrap_fullwidth(text)
    stripped = "".join(char for char in unwrapped if not should_strip(char))
    return collapse_ws(stripped)


def sanitize(response_text: str) -> str | None:
    """Strip foreign-script leaks outside markdown code. None if unchanged."""
    if not response_text:
        return None
    pieces = [
        chunk if kind == "code" else _clean_prose(chunk)
        for kind, chunk in split_markdown_code(response_text)
    ]
    cleaned = "".join(pieces)
    if cleaned != response_text:
        return cleaned.strip()
    return None
