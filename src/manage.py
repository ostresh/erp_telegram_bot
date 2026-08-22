"""
Управление проектом.

Запуск:
    python -m manage migrate init "Описание"
    python -m manage migrate upgrade
    python -m manage migrate downgrade
    python -m manage migrate history
    python -m manage migrate current
"""
import subprocess
import sys
from pathlib import Path

# Путь к alembic.ini
ALEMBIC_INI = Path(__file__).parent / "bot" / "db" / "alembic.ini"


def run_command(args: list[str]) -> int:
    """Запуск команды Alembic."""
    cmd = ["alembic", "-c", str(ALEMBIC_INI)] + args
    result = subprocess.run(cmd, cwd=str(ALEMBIC_INI.parent))
    return result.returncode


def handle_migrate(args: list[str]) -> int:
    """Обработка команды migrate."""
    if not args:
        print("""
Использование: python -m manage migrate <command> [message]

Команды:
  init <message>      Создать миграцию (autogenerate)
  upgrade [N|head]    Применить миграции (по умолчанию: head)
  downgrade [N|-1]    Откатить миграции (по умолчанию: -1)
  current             Текущая версия БД
  history             История миграций
  check               Проверить разницу моделей и БД
  sql                 Генерировать SQL без применения

Примеры:
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
            print("❌ Укажи описание: python -m manage migrate init 'Описание'")
            return 1
        message = " ".join(args[1:])
        return run_command(["revision", "--autogenerate", "-m", message])
    
    elif command == "upgrade":
        target = args[1] if len(args) > 1 else "head"
        return run_command(["upgrade", target])
    
    elif command == "downgrade":
        target = args[1] if len(args) > 1 else "-1"
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
        print(f"❌ Неизвестная команда: {command}")
        return 1


def main():
    if len(sys.argv) < 2:
        print("""
Управление проектом ERP Telegram Bot

Использование: python -m manage <command>

Команды:
  migrate    Управление миграциями БД (Alembic)
  run        Запуск бота
  test       Запуск playground

Примеры:
  python -m manage migrate init "Initial tables"
  python -m manage migrate upgrade
  python -m manage run
        """)
        return
    
    command = sys.argv[1]
    
    if command == "migrate":
        sys.exit(handle_migrate(sys.argv[2:]))
    
    elif command == "run":
        subprocess.run(["python", "-m", "main"])
    
    elif command == "test":
        subprocess.run(["python", "-m", "playground"])
    
    else:
        print(f"❌ Неизвестная команда: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()