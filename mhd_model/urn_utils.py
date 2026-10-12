import re
import urllib.parse
from re import Pattern

from cachetools import cached

# Characters in 'pchar' outside RFC 3986 unreserved [a-zA-Z0-9_.-~]
_PCHAR_SAFE: str = "!$&'()*+,;=:@"
# Subsequent characters in NSS also allow unencoded '/'
_NSS_SUBSEQUENT_SAFE: str = _PCHAR_SAFE + "/"
# Matches an existing percent-encoded triplet (e.g., %20, %2f)
_PCT_ENCODED_RE: Pattern[str] = re.compile(r"%([0-9a-fA-F]{2})")
# RFC 8141 NSS validation pattern (canonical uppercase hex digits)
RFC8141_NSS_PATTERN: Pattern[str] = re.compile(
    r"^(?:[a-zA-Z0-9._~-]|[!$&'()*+,;=:@]|%[0-9A-F]{2})"
    r"(?:[a-zA-Z0-9._~-]|[!$&'()*+,;=:@/]|%[0-9A-F]{2})*$"
)

RFC8141_NID_SYNTAX_PATTERN: Pattern[str] = re.compile(
    r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,30}[a-zA-Z0-9]$"
)


@cached(cache={})
def check_rfc8141_nid(value: str):
    return bool(RFC8141_NID_SYNTAX_PATTERN.fullmatch(value))


def to_rfc8141_nss(
    value: str,
    *,
    preserve_existing_encodings: bool = False,
) -> str:
    """Convert an arbitrary string into an RFC 8141 NSS compliant string.
    Args:
        value: The input string to convert.
        preserve_existing_encodings: When True, preserves valid existing
            percent-encoded sequences (%XX) and normalizes their hex digits
            to uppercase. When False (default), percent-encodes all raw
            characters (including any literal '%').
    Returns:
        A compliant RFC 8141 Namespace Specific String (NSS).
    Raises:
        ValueError: If `value` is empty (RFC 8141 requires at least one pchar).
    """
    if not value:
        raise ValueError("An RFC 8141 NSS cannot be empty.")
    if not preserve_existing_encodings:
        # Initial character must be pchar (slash '/' is not allowed unencoded)
        first_token: str = urllib.parse.quote(value[0], safe=_PCHAR_SAFE)
        # Subsequent characters allow pchar and '/'
        subsequent_tokens: str = (
            urllib.parse.quote(value[1:], safe=_NSS_SUBSEQUENT_SAFE)
            if len(value) > 1
            else ""
        )
        return first_token + subsequent_tokens
    # Preserving existing valid percent-encodings
    result: list[str] = []
    index: int = 0
    total_length: int = len(value)
    is_first_token: bool = True
    while index < total_length:
        pct_match: None | re.Match[str] = _PCT_ENCODED_RE.match(value, index)
        if pct_match is not None:
            # Uppercase hex digits per RFC 8141 Section 3.1
            result.append(f"%{pct_match.group(1).upper()}")
            index += 3
            is_first_token = False
            continue
        char: str = value[index]
        safe_chars: str = _PCHAR_SAFE if is_first_token else _NSS_SUBSEQUENT_SAFE
        result.append(urllib.parse.quote(char, safe=safe_chars))
        index += 1
        is_first_token = False
    return "".join(result)


def is_valid_rfc8141_nss(value: str) -> bool:
    """Validate whether a string conforms to the RFC 8141 NSS ABNF grammar.
    Args:
        value: The string to test.
    Returns:
        True if the string complies with RFC 8141 NSS, False otherwise.
    """
    return bool(RFC8141_NSS_PATTERN.fullmatch(value))
