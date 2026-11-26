from functools import lru_cache
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_REGULAR = "LabelSans"
FONT_BOLD = "LabelSans-Bold"

_ASSETS = Path(__file__).parent / "assets"
_REGULAR_FILE = "LiberationSans-Regular.ttf"
_BOLD_FILE = "LiberationSans-Bold.ttf"


@lru_cache(maxsize=1)
def register_fonts() -> None:
    """
    Регистрирует TTF-шрифты с кириллицей в ReportLab.

    Выполняется один раз за процесс благодаря lru_cache.
    Liberation Sans метрически совместим с Arial из шаблонов.

    Raises:
        FileNotFoundError: если файлов шрифтов нет в assets
    """
    regular = _ASSETS / _REGULAR_FILE
    bold = _ASSETS / _BOLD_FILE

    missing = [str(p) for p in (regular, bold) if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Не найдены файлы шрифтов: " + ", ".join(missing)
        )

    pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(regular)))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))