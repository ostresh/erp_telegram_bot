from dataclasses import dataclass

from reportlab.lib.units import mm


@dataclass(frozen=True)
class Box:
    """
    Прямоугольник элемента в миллиметрах.

    Left/Top считаются от левого верхнего угла этикетки.
    """

    left: float
    top: float
    width: float
    height: float

    @property
    def x(self) -> float:
        """Левая граница в точках PDF."""
        return self.left * mm

    @property
    def w(self) -> float:
        """Ширина в точках PDF."""
        return self.width * mm

    @property
    def h(self) -> float:
        """Высота в точках PDF."""
        return self.height * mm


@dataclass(frozen=True)
class LabelLayout:
    """
    Геометрия этикетки. Размеры полей — в мм, кегли — в пунктах.

    Attributes:
        width_mm, height_mm: размер этикетки
        title: поле названия доставки
        code: поле штрихкода или QR
        items: поле списка позиций
        items_rotation: поворот поля позиций в градусах (Orientation из XML)
    """

    width_mm: float
    height_mm: float
    title: Box
    title_font_size: float
    code: Box
    code_font_size: float
    items: Box
    items_font_size: float
    items_rotation: int = 0

    @property
    def pagesize(self) -> tuple[float, float]:
        """Размер страницы PDF в точках."""
        return (self.width_mm * mm, self.height_mm * mm)


# Штрих.xml: 58x40, заголовок 2/1/56/5 Arial 10 Bold,
# Code128 2/6/56/16 HRI 5, игры 2/23/56/17 Arial 6
BARCODE_LAYOUT = LabelLayout(
    width_mm=58,
    height_mm=40,
    title=Box(left=2, top=1, width=56, height=5),
    title_font_size=10,
    code=Box(left=2, top=6, width=56, height=16),
    code_font_size=5,
    items=Box(left=2, top=23, width=56, height=17),
    items_font_size=6,
)

# qr.xml: 58x40, заголовок 2/1/33/5 Arial 10 Bold,
# QR 2/6/33/34, игры 36/2/22/36 Arial 6 Orientation 270
QR_LAYOUT = LabelLayout(
    width_mm=58,
    height_mm=40,
    title=Box(left=2, top=1, width=33, height=5),
    title_font_size=10,
    code=Box(left=2, top=5, width=33, height=34),
    code_font_size=7,
    items=Box(left=36, top=2, width=20, height=36),
    items_font_size=6,
    items_rotation=90,
)