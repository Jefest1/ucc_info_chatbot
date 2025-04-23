import hashlib

_seen_hashes = set()


def is_duplicate(content: str) -> bool:
    """Return True if content has been seen before."""
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if h in _seen_hashes:
        return True
    _seen_hashes.add(h)
    return False
