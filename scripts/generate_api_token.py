"""
Генерация API-токена и его SHA-256 хеша.

Использование:
    python scripts/generate_api_token.py
"""

import hashlib
import secrets


def main() -> None:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    print("API_TOKEN=" + token)
    print("API_TOKEN_SHA256=" + token_hash)


if __name__ == "__main__":
    main()