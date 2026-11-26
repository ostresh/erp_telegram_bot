import logging
from collections.abc import Sequence
from io import BytesIO

from reportlab.pdfgen import canvas

from app.core.dto.labels import LabelDTO
from app.core.service.labels.layout import BARCODE_LAYOUT
from app.core.service.labels.mapping import get_label_mode
from app.core.service.labels.render import get_renderer

logger = logging.getLogger(__name__)


class LabelService:
    """
    Сервис генерации PDF с этикетками.

    Не зависит от интерфейсов: на вход список DTO, на выход байты PDF.
    Один DTO — одна страница размером с этикетку.
    """

    def generate(self, labels: Sequence[LabelDTO]) -> bytes:
        """
        Формирует PDF со всеми этикетками.

        Args:
            labels: Список данных этикеток

        Returns:
            Байты готового PDF

        Raises:
            ValueError: если список пуст или режим доставки не определен
            FileNotFoundError: если отсутствуют файлы шрифтов
        """
        if not labels:
            raise ValueError("Список этикеток пуст")

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=BARCODE_LAYOUT.pagesize)
        c.setTitle("Этикетки")

        try:
            for label in labels:
                renderer = get_renderer(get_label_mode(label.delivery))
                c.setPageSize(renderer.layout.pagesize)
                renderer.draw(c, label)
                c.showPage()
            c.save()
        except Exception:
            logger.exception("Ошибка генерации этикеток")
            raise

        logger.info(f"Labels PDF generated: {len(labels)} labels")
        return buffer.getvalue()