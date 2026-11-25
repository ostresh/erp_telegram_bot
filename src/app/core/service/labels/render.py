from __future__ import annotations

from abc import ABC, abstractmethod

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.code128 import Code128
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from app.core.dto.labels import LabelDTO
from app.core.service.labels.fonts import FONT_BOLD, FONT_REGULAR, register_fonts
from app.core.service.labels.layout import BARCODE_LAYOUT, QR_LAYOUT, LabelLayout
from app.core.service.labels.mapping import LabelMode

LINE_LEADING = 1.2
ELLIPSIS = "…"
QTY_TEMPLATE = "{name} х{count}"
QR_QUIET_MODULES = 2        # тихая зона QR в модулях (было 4) — белое поле вокруг кода
HRI_BOTTOM_PAD = 1.2 * mm   # отступ номера от нижнего края поля
HRI_GAP = 0.8 * mm          # зазор между номером и QR


def _ascent(font_name: str, size: float) -> float:
    """Высота символов над базовой линией в пунктах."""
    return pdfmetrics.getAscent(font_name) / 1000.0 * size


def _truncate(text: str, max_width: float, font_name: str, size: float) -> str:
    """Обрезает строку по ширине поля, добавляя многоточие."""
    if pdfmetrics.stringWidth(text, font_name, size) <= max_width:
        return text
    while text and pdfmetrics.stringWidth(text + ELLIPSIS, font_name, size) > max_width:
        text = text[:-1]
    return text + ELLIPSIS


def _force_ellipsis(text: str, max_width: float, font_name: str, size: float) -> str:
    """Гарантированно ставит многоточие в конце строки."""
    text = text.removesuffix(ELLIPSIS)
    while text and pdfmetrics.stringWidth(text + ELLIPSIS, font_name, size) > max_width:
        text = text[:-1]
    return text + ELLIPSIS


class BaseLabelRenderer(ABC):
    """
    Базовый рендерер этикетки.

    Задает шаблон: draw() рисует заголовок, код и список позиций,
    способ отрисовки кода определяет подкласс.
    """

    layout: LabelLayout

    def draw(self, c: canvas.Canvas, label: LabelDTO) -> None:
        """
        Рисует одну этикетку на текущей странице canvas.

        Args:
            c: Канва PDF
            label: Данные этикетки
        """
        register_fonts()
        self._draw_title(c, label.delivery.display_name)
        self._draw_code(c, label.order_number)
        self._draw_items(
            c,
            [QTY_TEMPLATE.format(name=i.game_name, count=i.count) for i in label.items],
        )

    @abstractmethod
    def _draw_code(self, c: canvas.Canvas, value: str) -> None:
        """Рисует штрихкод или QR в поле code."""

    @property
    def _page_h(self) -> float:
        """Высота страницы в пунктах."""
        return self.layout.height_mm * mm

    def _draw_title(self, c: canvas.Canvas, text: str) -> None:
        """Рисует название доставки: Arial 10 Bold, прижат к левому верху поля."""
        box = self.layout.title
        size = self.layout.title_font_size
        text = _truncate(text, box.w, FONT_BOLD, size)

        c.setFont(FONT_BOLD, size)
        c.drawString(box.x, self._page_h - box.top * mm - _ascent(FONT_BOLD, size), text)

    def _draw_items(self, c: canvas.Canvas, lines: list[str]) -> None:
        """
        Рисует список позиций построчно с количеством.

        Для повернутого поля длина строки идет вдоль высоты бокса,
        а строки укладываются по его ширине. Не влезшее обрезается с многоточием.

        Поворот 270: чтение сверху вниз, первая строка у правого края поля.
        Поворот 90: чтение снизу вверх, первая строка у левого края поля.
        """
        box = self.layout.items
        size = self.layout.items_font_size
        leading = size * LINE_LEADING
        rotation = self.layout.items_rotation
        rotated = rotation in (90, 270)

        max_width = box.h if rotated else box.w
        max_lines = int((box.w if rotated else box.h) // leading)
        prepared = self._fit_lines(lines, max_width, max_lines, size)
        if not prepared:
            return

        c.saveState()
        if rotation == 270:
            c.translate(box.x + box.w, self._page_h - box.top * mm)
        elif rotation == 90:
            c.translate(box.x, self._page_h - (box.top + box.height) * mm)
        else:
            c.translate(box.x, self._page_h - box.top * mm)
        c.rotate(rotation)

        c.setFont(FONT_REGULAR, size)
        y = -_ascent(FONT_REGULAR, size)
        for line in prepared:
            c.drawString(0, y, line)
            y -= leading
        c.restoreState()

    def _fit_lines(
        self,
        lines: list[str],
        max_width: float,
        max_lines: int,
        size: float,
    ) -> list[str]:
        """Подгоняет список строк под ширину и высоту поля."""
        if max_lines <= 0:
            return []

        fitted = [_truncate(t, max_width, FONT_REGULAR, size) for t in lines]
        if len(fitted) <= max_lines:
            return fitted

        visible = fitted[:max_lines]
        visible[-1] = _force_ellipsis(visible[-1], max_width, FONT_REGULAR, size)
        return visible


class BarcodeLabelRenderer(BaseLabelRenderer):
    """Этикетка с Code128 и цифрами под штрихами (PrintHRI)."""

    layout = BARCODE_LAYOUT

    def _draw_code(self, c: canvas.Canvas, value: str) -> None:
        box = self.layout.code
        hri_size = self.layout.code_font_size
        bar_height = box.h - hri_size * LINE_LEADING

        barcode = self._fit_code128(value, box.w, bar_height)
        top_y = self._page_h - box.top * mm
        bars_y = top_y - bar_height

        barcode.drawOn(c, box.x + (box.w - barcode.width) / 2, bars_y)

        c.setFont(FONT_REGULAR, hri_size)
        c.drawCentredString(box.x + box.w / 2, bars_y - hri_size, value)

    @staticmethod
    def _fit_code128(value: str, max_width: float, bar_height: float) -> Code128:
        """
        Подбирает толщину штриха так, чтобы код с quiet zone влез в поле.

        При barWidth=1 ширина виджета равна числу модулей,
        дальше масштаб линейный.
        """
        probe = Code128(value, barWidth=1, barHeight=bar_height, quiet=True)
        modules = probe.width
        if modules <= 0:
            raise ValueError(f"Не удалось построить штрихкод для {value!r}")
        return Code128(value, barWidth=max_width / modules, barHeight=bar_height, quiet=True)


class QrLabelRenderer(BaseLabelRenderer):
    """Этикетка с QR-кодом и номером заказа под ним."""

    layout = QR_LAYOUT

    def _draw_code(self, c: canvas.Canvas, value: str) -> None:
        box = self.layout.code
        hri_size = self.layout.code_font_size

        # номер заказа: отступ от нижнего края поля, целиком внутри этикетки
        hri_baseline = self._page_h - (box.top + box.height) * mm + HRI_BOTTOM_PAD
        qr_bottom = hri_baseline + _ascent(FONT_REGULAR, hri_size) + HRI_GAP

        # QR квадратный, занимает все место от зазора до верха поля
        box_top = self._page_h - box.top * mm
        side = min(box.w, box_top - qr_bottom)

        qr = QrCodeWidget(value, barLevel="M", barBorder=QR_QUIET_MODULES)
        x1, y1, x2, y2 = qr.getBounds()
        w, h = x2 - x1, y2 - y1
        if w <= 0 or h <= 0:
            raise ValueError(f"Не удалось построить QR для {value!r}")

        drawing = Drawing(side, side, transform=[side / w, 0, 0, side / h, 0, 0])
        drawing.add(qr)
        renderPDF.draw(drawing, c, box.x + (box.w - side) / 2, qr_bottom)

        # номер по центру поля, под QR, с отступами
        text = _truncate(value, box.w, FONT_REGULAR, hri_size)
        c.setFont(FONT_REGULAR, hri_size)
        c.drawCentredString(box.x + box.w / 2, hri_baseline, text)


_RENDERERS: dict[LabelMode, type[BaseLabelRenderer]] = {
    LabelMode.BARCODE: BarcodeLabelRenderer,
    LabelMode.QR: QrLabelRenderer,
}


def get_renderer(mode: LabelMode) -> BaseLabelRenderer:
    """
    Возвращает рендерер под режим этикетки.

    Args:
        mode: Режим этикетки

    Returns:
        Экземпляр рендерера

    Raises:
        ValueError: если режим не поддерживается
    """
    renderer_cls = _RENDERERS.get(mode)
    if renderer_cls is None:
        raise ValueError(f"Неизвестный режим этикетки: {mode}")
    return renderer_cls()