import pytest
from app.interfaces.api.config import ApiConfigError, load_api_config

@pytest.fixture
def no_api_env(monkeypatch):
    """Убираем переменные окружения"""
    for var in ("API_TOKEN", "API_TOKEN_SHA256", "ENVIRONMENT", "API_MAX_TOKEN_LENGTH"):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch

def test_valid_raw_token(no_api_env):
    """Raw token в development"""
    cfg = load_api_config(
        _env_file=None,
        environment="development",
        api_token="x" * 40
        )
    
    assert cfg.environment == "development"
    assert cfg.auth_mode == "raw_token"
    assert cfg.api_token == "x" * 40
    assert cfg.api_token_sha256 is None
    assert not cfg.is_production
    
def test_valid_hash(no_api_env):
    cfg = load_api_config(
        _env_file=None,
        environment="development",
        api_token_sha256="a" * 64
    )
    
    assert cfg.environment == "development"
    assert cfg.auth_mode == "token_hash"
    assert cfg.api_token is None
    assert cfg.api_token_sha256 == "a" * 64
    
def test_prod_with_hash_ok(no_api_env):
    cfg = load_api_config(
        _env_file=None,
        environment="production",
        api_token_sha256="a" * 64
    )
    
    assert cfg.is_production
    assert cfg.auth_mode == "token_hash"
    
def test_default_environment_is_development(no_api_env):
    """Если ENVIRONMENT не задан, используется development."""
    cfg = load_api_config(
        _env_file=None,
        api_token="x" * 40,
    )

    assert cfg.environment == "development"
    assert not cfg.is_production


def test_default_max_token_length(no_api_env):
    """Если API_MAX_TOKEN_LENGTH не задан, используется 256."""
    cfg = load_api_config(
        _env_file=None,
        api_token="x" * 40,
    )

    assert cfg.max_token_length == 256


def test_custom_max_token_length(no_api_env):
    """API_MAX_TOKEN_LENGTH можно переопределить."""
    cfg = load_api_config(
        _env_file=None,
        api_token="x" * 40,
        max_token_length=512,
    )

    assert cfg.max_token_length == 512


def test_min_length_token_accepted(no_api_env):
    """Токен минимальной длины принимается."""
    cfg = load_api_config(
        _env_file=None,
        api_token="x" * 32,
    )

    assert cfg.api_token == "x" * 32


def test_hash_is_lowercased(no_api_env):
    """Хеш приводится к нижнему регистру."""
    cfg = load_api_config(
        _env_file=None,
        api_token_sha256="A" * 64,
    )

    assert cfg.api_token_sha256 == "a" * 64
    assert cfg.token_hash_bytes == bytes.fromhex("a" * 64)


def test_token_hash_bytes_in_hash_mode(no_api_env):
    """В режиме хеша token_hash_bytes возвращает bytes."""
    cfg = load_api_config(
        _env_file=None,
        api_token_sha256="a" * 64,
    )

    assert cfg.token_hash_bytes == bytes.fromhex("a" * 64)


def test_token_hash_bytes_is_none_in_raw_mode(no_api_env):
    """В режиме сырого токена token_hash_bytes возвращает None."""
    cfg = load_api_config(
        _env_file=None,
        api_token="x" * 40,
    )

    assert cfg.token_hash_bytes is None
    
def test_no_secret_rejected(no_api_env):
    with pytest.raises(ApiConfigError, match="Секрет аутентификации не настроен"):
        load_api_config(_env_file=None)
        
def test_empty_raw_token_rejected(no_api_env):
    """Пустой API_TOKEN считается отсутствующим."""
    with pytest.raises(ApiConfigError, match="Секрет аутентификации не настроен"):
        load_api_config(
            _env_file=None,
            api_token="",
        )


def test_empty_hash_rejected(no_api_env):
    """Пустой API_TOKEN_SHA256 считается отсутствующим."""
    with pytest.raises(ApiConfigError, match="Секрет аутентификации не настроен"):
        load_api_config(
            _env_file=None,
            api_token_sha256="",
        )


def test_whitespace_raw_token_rejected(no_api_env):
    """API_TOKEN из пробелов считается отсутствующим."""
    with pytest.raises(ApiConfigError, match="Секрет аутентификации не настроен"):
        load_api_config(
            _env_file=None,
            api_token="   ",
        )


def test_whitespace_hash_rejected(no_api_env):
    """API_TOKEN_SHA256 из пробелов считается отсутствующим."""
    with pytest.raises(ApiConfigError, match="Секрет аутентификации не настроен"):
        load_api_config(
            _env_file=None,
            api_token_sha256="   ",
        )


# ---------------------------------------------------------------------------
# Ошибки: оба секрета сразу
# ---------------------------------------------------------------------------


def test_both_secrets_rejected(no_api_env):
    """Нельзя задать API_TOKEN и API_TOKEN_SHA256 одновременно."""
    with pytest.raises(
        ApiConfigError,
        match="Заданы одновременно API_TOKEN и API_TOKEN_SHA256",
    ):
        load_api_config(
            _env_file=None,
            api_token="x" * 40,
            api_token_sha256="a" * 64,
        )


# ---------------------------------------------------------------------------
# Ошибки: production
# ---------------------------------------------------------------------------


def test_prod_with_raw_token_rejected(no_api_env):
    """Сырой API_TOKEN запрещён в production."""
    with pytest.raises(
        ApiConfigError,
        match="Сырой API_TOKEN запрещён в production",
    ):
        load_api_config(
            _env_file=None,
            environment="production",
            api_token="x" * 40,
        )


def test_prod_without_secret_rejected(no_api_env):
    """Production без секрета невалиден."""
    with pytest.raises(ApiConfigError, match="Секрет аутентификации не настроен"):
        load_api_config(
            _env_file=None,
            environment="production",
        )


# ---------------------------------------------------------------------------
# Ошибки: длина токена
# ---------------------------------------------------------------------------


def test_short_raw_token_rejected(no_api_env):
    """Слишком короткий API_TOKEN отклоняется."""
    with pytest.raises(ApiConfigError, match="API_TOKEN слишком короткий"):
        load_api_config(
            _env_file=None,
            api_token="short",
        )


def test_raw_token_longer_than_max_length_rejected(no_api_env):
    """API_TOKEN не может быть длиннее API_MAX_TOKEN_LENGTH."""
    with pytest.raises(
        ApiConfigError,
        match="API_TOKEN длиннее API_MAX_TOKEN_LENGTH",
    ):
        load_api_config(
            _env_file=None,
            api_token="x" * 300,
            max_token_length=256,
        )


# ---------------------------------------------------------------------------
# Ошибки: формат хеша
# ---------------------------------------------------------------------------


def test_invalid_hash_length_rejected(no_api_env):
    """Хеш неверной длины отклоняется."""
    with pytest.raises(
        ApiConfigError,
        match="API_TOKEN_SHA256 должен быть строкой из 64 hex-символов",
    ):
        load_api_config(
            _env_file=None,
            api_token_sha256="abc",
        )


def test_invalid_hash_characters_rejected(no_api_env):
    """Хеш с не-hex символами отклоняется."""
    with pytest.raises(
        ApiConfigError,
        match="API_TOKEN_SHA256 не является корректной hex-строкой",
    ):
        load_api_config(
            _env_file=None,
            api_token_sha256="z" * 64,
        )


# ---------------------------------------------------------------------------
# Ошибки: max_token_length
# ---------------------------------------------------------------------------


def test_max_token_length_too_small_rejected(no_api_env):
    """API_MAX_TOKEN_LENGTH меньше минимума отклоняется."""
    with pytest.raises(
        ApiConfigError,
        match="API_MAX_TOKEN_LENGTH должен быть в диапазоне",
    ):
        load_api_config(
            _env_file=None,
            api_token="x" * 40,
            max_token_length=10,
        )


def test_max_token_length_too_large_rejected(no_api_env):
    """API_MAX_TOKEN_LENGTH больше максимума отклоняется."""
    with pytest.raises(
        ApiConfigError,
        match="API_MAX_TOKEN_LENGTH должен быть в диапазоне ",
    ):
        load_api_config(
            _env_file=None,
            api_token="x" * 40,
            max_token_length=10000,
        )


# ---------------------------------------------------------------------------
# Ошибки: environment
# ---------------------------------------------------------------------------


def test_invalid_environment_rejected(no_api_env):
    """Недопустимое значение ENVIRONMENT отклоняется."""
    with pytest.raises(ApiConfigError):
        load_api_config(
            _env_file=None,
            environment="prod",
            api_token_sha256="a" * 64,
        )


def test_environment_is_normalized_before_literal_validation(no_api_env):
    """ENVIRONMENT=PRODUCTION должен быть принят после нормализации."""
    cfg = load_api_config(
        _env_file=None,
        environment="PRODUCTION",
        api_token_sha256="a" * 64,
    )

    assert cfg.environment == "production"
    assert cfg.is_production


# ---------------------------------------------------------------------------
# Безопасность сообщений об ошибках
# ---------------------------------------------------------------------------


def test_error_message_does_not_leak_raw_secret(no_api_env):
    """
    Сообщение об ошибке не должно содержать сам секрет.

    Это важно, потому что ошибки конфигурации могут попасть в логи.
    """
    secret = "super-secret-token-12345678901234567890"

    with pytest.raises(ApiConfigError) as exc_info:
        load_api_config(
            _env_file=None,
            api_token=secret,
            api_token_sha256="a" * 64,
        )

    error_message = str(exc_info.value)

    assert secret not in error_message
    assert "super-secret" not in error_message


def test_error_message_does_not_leak_hash_secret(no_api_env):
    """
    Сообщение об ошибке не должно содержать хеш токена.

    Даже хеш в логах лучше не светить без необходимости.
    """
    secret_hash = "b" * 64

    with pytest.raises(ApiConfigError) as exc_info:
        load_api_config(
            _env_file=None,
            api_token="x" * 40,
            api_token_sha256=secret_hash,
        )

    error_message = str(exc_info.value)

    assert secret_hash not in error_message