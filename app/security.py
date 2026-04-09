import hashlib


def sha1_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest().upper()


def split_hash_prefix_suffix(hash_value: str) -> tuple[str, str]:
    prefix = hash_value[:5]
    suffix = hash_value[5:]
    return prefix, suffix
