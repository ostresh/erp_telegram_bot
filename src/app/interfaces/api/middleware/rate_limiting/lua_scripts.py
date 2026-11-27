
# Lua-скрипт для атомарной проверки лимита
RATE_LIMIT_LUA_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Удаляем записи старше окна
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

-- Всегда добавляем запись, чтобы счётчик отражал реальное число запросов в окне
-- (иначе при достижении лимита счётчик «залипает» на limit и блокировка недостижима).
-- Используем now-random как уникальный member
local member = now .. '-' .. tostring(math.random(1000000))
redis.call('ZADD', key, now, member)

-- Считаем текущее количество запросов, включая только что добавленный
local count = redis.call('ZCARD', key)

-- Устанавливаем TTL на случай, если запросы прекратятся
redis.call('EXPIRE', key, window + 1)

return count
"""
