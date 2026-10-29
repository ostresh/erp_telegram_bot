from __future__ import annotations
from typing import Any, Literal

from pydantic import Field, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Минимально допустимая длина сырого токена.
MIN_TOKEN_LENGTH = 32
# Верхняя граница для настройки API_MAX_TOKEN_LENGTH.
MAX_TOKEN_LENGTH_LIMIT = 4096
# Лимит длины входящего токена по умолчанию.
DEFAULT_MAX_TOKEN_LENGTH = 256
# SHA-256 digest в hex всегда занимает 64 символа.
SHA256_HEX_LENGTH = 64


class ApiConfigError(RuntimeError):
    """Невалидная конфигурация безопасности API. Приложение не должно стартовать."""


class ApiConfig(BaseSettings):
    """
    Прошлифованная конфигурация аутентификации API.

    Важно:
    - секреты читаются только из окружения / .env;
    - в коде секретов нет;
    - при невалидной конфигурации создание объекта падает;
    - сообщения об ошибках не должны раскрывать значения секретов.
    """
    
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        populate_by_name=True
    )
    
    environment: Literal["development", "production"] = "development"
    
    api_token: str | None = None
    api_token_sha256: str | None = None
    
    max_token_length: int = Field(
        default=DEFAULT_MAX_TOKEN_LENGTH,
        alias="API_MAX_TOKEN_LENGTH"
    )
    
    # Префикс всех маршрутов API.
    api_prefix: str = "/api/v1"

    # Показывать ли /docs и /openapi.json (в production отключается всегда).
    api_docs_enabled: bool = True
    
    
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="CELERY_BROKER_URL"
    )
    # нормализация
    
    @field_validator("environment", mode="before")
    @classmethod
    def _normalize_environment(cls, value):
        """
        Приводит ENVIRONMENT к нижнему регистру.
        """
        if value is None:
            return "development"
        return str(value).strip().lower()

    @field_validator("api_token", "api_token_sha256", mode="before")
    @classmethod
    def _empty_to_none(cls, value):
        """Пустая строка и строка из пробелов считаем «не задано»."""
        if isinstance(value, str):
            return value.strip() or None
        return value
    
    
    # валидация
    
    @field_validator("api_token")
    @classmethod
    def _check_token(cls, value):
        if value is not None and len(value) < MIN_TOKEN_LENGTH:
            raise ValueError(
                f"API_TOKEN слишком короткий: минимум {MIN_TOKEN_LENGTH} символов"
            )
        return value

    @field_validator("api_token_sha256")
    @classmethod
    def _check_token_hash(cls, value):
        if value is None:
            return value
        
        normalized = value.lower()
        
        if len(normalized) != SHA256_HEX_LENGTH:
            raise ValueError(
                f"API_TOKEN_SHA256 должен быть строкой из {SHA256_HEX_LENGTH} hex-символов"
            )
            
        try:
            bytes.fromhex(normalized)
        except ValueError as exc:
            raise ValueError("API_TOKEN_SHA256 не является корректной hex-строкой") from exc
        
        return normalized
    
    @field_validator("max_token_length")
    @classmethod
    def _check_max_token_length(cls, value: int) -> int:
        if not MIN_TOKEN_LENGTH <= value <= MAX_TOKEN_LENGTH_LIMIT:
            raise ValueError(
                f"API_MAX_TOKEN_LENGTH должен быть в диапазоне "
                f"{MIN_TOKEN_LENGTH}..{MAX_TOKEN_LENGTH_LIMIT}"
            )
        return value
    
    
    # правила безопасности
    
    @model_validator(mode="after")
    def _security_rules(self) -> "ApiConfig":
        """
        Правила, которые нельзя проверить в одном поле.

        Здесь экземпляр уже создан, все поля уже нормализованы
        и прошли индивидуальную валидацию.
        """

        # Нельзя одновременно сырой токен и его хеш.
        if self.api_token is not None and self.api_token_sha256 is not None:
            raise ValueError(
                "Заданы одновременно API_TOKEN и API_TOKEN_SHA256: "
                "нужно ровно одно"
            )

        # Секрет обязан существовать.
        if self.api_token is None and self.api_token_sha256 is None:
            raise ValueError(
                "Секрет аутентификации не настроен: "
                "укажите API_TOKEN (dev) или API_TOKEN_SHA256 (prod)"
            )

        # В production сырой токен запрещён.
        if self.is_production and self.api_token is not None:
            raise ValueError(
                "Сырой API_TOKEN запрещён в production: "
                "используйте API_TOKEN_SHA256"
            )

        # Настроенный токен не должен быть длиннее собственного лимита.
        # Иначе все валидные запросы будут отклоняться.
        if (
            self.api_token is not None
            and len(self.api_token) > self.max_token_length
        ):
            raise ValueError(
                "API_TOKEN длиннее API_MAX_TOKEN_LENGTH: "
                "все запросы с этим токеном будут отклонены"
            )

        return self
    
    # проверти методы
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def auth_mode(self) -> str:
        return "token_hash" if self.api_token_sha256 is not None else "raw_token"
    
    @property
    def token_hash_bytes(self) -> bytes | None:
        """SHA-256 digest в виде байтов. В режиме сырого токена - None"""
        if self.api_token_sha256 is None:
            return None
        return bytes.fromhex(self.api_token_sha256)
    
def load_api_config(**overrides: Any) -> ApiConfig:
    """Создает конфигурацию"""
    
    try:
        return ApiConfig(**overrides)
    except ValidationError as exc:
        details = "; ".join(
            f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}"
            for err in exc.errors()
        )
        raise ApiConfigError(f"Невалидная конфигурация API: {details}") from None
    
api_config = load_api_config()