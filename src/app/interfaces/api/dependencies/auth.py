from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.interfaces.api.config import api_config

bearer_scheme = HTTPBearer(auto_error=False)

DEFAULT_KEY_ID = "default"

@dataclass(frozen=True)
class CurrentIdentity:
    """
    Кто выполняет запрос
    
    Attributes:
        key_id (str): id ключа
    """
    
    key_id: str
    
def unauthorized() -> HTTPException:
    """
    Единая ошибка аутентификации
    """
    
    return HTTPException(
        status_code=401,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
def _verify_token(token: str) -> bool:
    """
    Сверяет входящий токен с секретом
    
    Возвращает True/False, никаких исключений и никакого логирования.
    Сравнение выполняется через hmac.compare_digest — сравнение
    с постоянным временем, чтобы не дать атакующему информацию
    по времени ответа.
    """
    
    expected = api_config.token_hash_bytes
    if expected is not None:
        # Режим хеша: хешируем входящий токен и сравниваем дайджесты.
        actual = hashlib.sha256(token.encode("utf-8")).digest()
    else:
        # Режим сырого токена (только разработка).
        expected = api_config.api_token.encode("utf-8")
        actual = token.encode("utf-8")
        
    return hmac.compare_digest(expected, actual)

async def get_current_identity(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
) -> CurrentIdentity:
    """
    FastAPI зависимость, проверяет запрос и возвращает личность клиента
    """
    
    # заголовка нет или схема не bearer
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized()
    
    token = credentials.credentials
    
    # пустой токен
    if not token:
        raise unauthorized()
    
    # слишком длинный токен
    if len(token) > api_config.max_token_length:
        raise unauthorized()
    
    # проверяем с секретом
    if not _verify_token(token):
        raise unauthorized()
    
    return CurrentIdentity(key_id=DEFAULT_KEY_ID)
    
    
    

