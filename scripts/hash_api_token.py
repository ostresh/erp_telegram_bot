"""
Считает SHA-256 хеш уже существующего токена.

Токен вводится скрытно и не остаётся в истории команд.
"""

import getpass
import hashlib


def main() -> None:
    token = getpass.getpass("Введи токен (символы не отображаются): ")
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    print("API_TOKEN_SHA256=" + token_hash)


if __name__ == "__main__":
    main()