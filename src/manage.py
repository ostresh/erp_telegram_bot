"""
Управление проектом.

Запуск:
    python -m manage migrate init "Описание"
    python -m manage migrate upgrade
    python -m manage migrate downgrade
    python -m manage migrate history
    python -m manage migrate current
    
    python -m manage run bot
    python -m manage run celery worker
    python -m manage run celery beat
    python -m manage run celery all
    
    python -m manage test
"""
import subprocess
import sys
import os
from pathlib import Path

# Путь к alembic.ini
ALEMBIC_INI = Path(__file__).parent / "bot" / "db" / "alembic.ini"

# Определяем платформу
IS_WINDOWS = sys.platform == "win32"


# === Цветной вывод ===

class Colors:
    """ANSI коды для цветного вывода"""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    
    # Активируем ANSI на Windows 10+
    if IS_WINDOWS:
        try:
            os.system("")
        except Exception:
            GREEN = YELLOW = BLUE = RED = CYAN = BOLD = RESET = ""


def log_info(msg: str) -> None:
    """Вывод информационного сообщения"""
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.RESET}")


def log_success(msg: str) -> None:
    """Вывод сообщения об успехе"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def log_error(msg: str) -> None:
    """Вывод сообщения об ошибке"""
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def log_warning(msg: str) -> None:
    """Вывод предупреждения"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


# === Запуск команд ===

def run_command(args: list[str]) -> int:
    """Запуск команды Alembic."""
    cmd = ["alembic", "-c", str(ALEMBIC_INI)] + args
    result = subprocess.run(cmd, cwd=str(ALEMBIC_INI.parent))
    return result.returncode


# === Команда migrate ===

def handle_migrate(args: list[str]) -> int:
    """Обработка команды migrate."""
    if not args:
        print(f"""
{Colors.BOLD}Использование:{Colors.RESET} python -m manage migrate <command> [message]

{Colors.BOLD}Команды:{Colors.RESET}
  {Colors.CYAN}init <message>{Colors.RESET}      Создать миграцию (autogenerate)
  {Colors.CYAN}upgrade [N|head]{Colors.RESET}    Применить миграции (по умолчанию: head)
  {Colors.CYAN}downgrade [N|-1]{Colors.RESET}    Откатить миграции (по умолчанию: -1)
  {Colors.CYAN}current{Colors.RESET}             Текущая версия БД
  {Colors.CYAN}history{Colors.RESET}             История миграций
  {Colors.CYAN}check{Colors.RESET}               Проверить разницу моделей и БД
  {Colors.CYAN}sql{Colors.RESET}                 Генерировать SQL без применения

{Colors.BOLD}Примеры:{Colors.RESET}
  python -m manage migrate init "Add email to records"
  python -m manage migrate upgrade
  python -m manage migrate upgrade head
  python -m manage migrate downgrade -1
  python -m manage migrate history
        """)
        return 0
    
    command = args[0]
    
    if command == "init":
        if len(args) < 2:
            log_error("Укажи описание: python -m manage migrate init 'Описание'")
            return 1
        message = " ".join(args[1:])
        log_info(f"Создание миграции: {message}")
        return run_command(["revision", "--autogenerate", "-m", message])
    
    elif command == "upgrade":
        target = args[1] if len(args) > 1 else "head"
        log_info(f"Применение миграций до: {target}")
        return run_command(["upgrade", target])
    
    elif command == "downgrade":
        target = args[1] if len(args) > 1 else "-1"
        log_info(f"Откат миграций: {target}")
        return run_command(["downgrade", target])
    
    elif command == "current":
        return run_command(["current"])
    
    elif command == "history":
        return run_command(["history", "--verbose"])
    
    elif command == "check":
        return run_command(["check"])
    
    elif command == "sql":
        return run_command(["upgrade", "head", "--sql"])
    
    else:
        log_error(f"Неизвестная команда: {command}")
        return 1


# === Команда run ===

def handle_run(args: list[str]) -> int:
    """Обработка команды run <app_name>."""
    if not args:
        print(f"""
{Colors.BOLD}Использование:{Colors.RESET} python -m manage run <app_name> [options]

{Colors.BOLD}Доступные приложения:{Colors.RESET}
  {Colors.CYAN}bot{Colors.RESET}                  Запуск Telegram бота
  {Colors.CYAN}celery worker{Colors.RESET}        Запуск Celery worker
  {Colors.CYAN}celery beat{Colors.RESET}          Запуск Celery beat (планировщик)
  {Colors.CYAN}celery all{Colors.RESET}           Запуск worker + beat вместе

{Colors.BOLD}Примеры:{Colors.RESET}
  python -m manage run bot
  python -m manage run celery worker
  python -m manage run celery beat
  python -m manage run celery all
        """)
        return 0
    
    app_name = args[0]
    
    # === Запуск бота ===
    if app_name == "bot":
        log_info("Запуск бота...")
        result = subprocess.run([sys.executable, "-m", "main"])
        return result.returncode
    
    # === Запуск Celery ===
    elif app_name == "celery":
        return handle_celery(args[1:])
    
    else:
        log_error(f"Неизвестное приложение: {app_name}")
        return 1


def handle_celery(args: list[str]) -> int:
    """Обработка команды run celery <command>."""
    if not args:
        print(f"""
{Colors.BOLD}Использование:{Colors.RESET} python -m manage run celery <command>

{Colors.BOLD}Команды:{Colors.RESET}
  {Colors.CYAN}worker{Colors.RESET}               Запуск Celery worker
  {Colors.CYAN}beat{Colors.RESET}                 Запуск Celery beat (планировщик)
  {Colors.CYAN}all{Colors.RESET}                  Запуск worker + beat вместе

{Colors.BOLD}Примеры:{Colors.RESET}
  python -m manage run celery worker
  python -m manage run celery beat
  python -m manage run celery all
        """)
        return 0
    
    command = args[0]
    
    # ✅ Путь к celery_app
    CELERY_APP = "app.tasks.celery_app"
    
    # ✅ Windows всегда использует solo pool
    pool_args = ["--pool=solo"] if IS_WINDOWS else []
    
    if command == "worker":
        log_info("Запуск Celery worker...")
        
        cmd = [
            "celery",
            "-A", CELERY_APP,
            "worker",
            "--loglevel=info",
        ] + pool_args
        
        if IS_WINDOWS:
            log_warning("Windows: используется --pool=solo")
        
        result = subprocess.run(cmd)
        return result.returncode
    
    elif command == "beat":
        log_info("Запуск Celery beat...")
        
        cmd = [
            "celery",
            "-A", CELERY_APP,
            "beat",
            "--loglevel=info",
        ]
        
        result = subprocess.run(cmd)
        return result.returncode
    
    elif command == "all":
        log_info("Запуск Celery worker + beat (один процесс)...")
        
        cmd = [
            "celery",
            "-A", CELERY_APP,
            "worker",
            "-B",  # Beat внутри worker
            "--loglevel=info",
        ] + pool_args
        
        if IS_WINDOWS:
            log_warning("Windows: используется --pool=solo")
        
        result = subprocess.run(cmd)
        return result.returncode
    
    else:
        log_error(f"Неизвестная celery команда: {command}")
        return 1

# === Команда test ===

def handle_test(args: list[str]) -> int:
    """Обработка команды test."""
    log_info("Запуск playground...")
    result = subprocess.run([sys.executable, "-m", "playground"])
    return result.returncode


# === Главный вывод справки ===

def print_main_help():
    """Вывод главной справки"""
    print(f"""
{Colors.BOLD}🚀 Управление проектом ERP Telegram Bot{Colors.RESET}

{Colors.BOLD}Использование:{Colors.RESET} python -m manage <command> [args]

{Colors.BOLD}Команды:{Colors.RESET}
  {Colors.CYAN}migrate{Colors.RESET}              Управление миграциями БД (Alembic)
  {Colors.CYAN}run <app>{Colors.RESET}            Запуск приложений (bot, celery)
  {Colors.CYAN}test{Colors.RESET}                 Запуск playground

{Colors.BOLD}Примеры:{Colors.RESET}
  python -m manage migrate init "Initial tables"
  python -m manage migrate upgrade
  python -m manage run bot
  python -m manage run celery all
  python -m manage test

{Colors.BOLD}Справка по команде:{Colors.RESET}
  python -m manage migrate
  python -m manage run
  python -m manage run celery
    """)


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print_main_help()
        return
    
    command = sys.argv[1]
    
    if command == "migrate":
        sys.exit(handle_migrate(sys.argv[2:]))
    
    elif command == "run":
        sys.exit(handle_run(sys.argv[2:]))
    
    elif command == "test":
        sys.exit(handle_test(sys.argv[2:]))
    
    elif command in ("help", "-h", "--help"):
        print_main_help()
    
    else:
        log_error(f"Неизвестная команда: {command}")
        print("Используй 'python -m manage' для списка команд")
        sys.exit(1)


if __name__ == "__main__":
    main()