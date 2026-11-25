from enum import Enum

from app.core.dto.labels import DeliveryType

class LabelMode(str, Enum):
    """Режим этикетки: штрихкод Code128 или QR"""
    
    BARCODE = "barcode"
    QR = "qr"

   
def get_label_mode(delivery: DeliveryType) -> str:
    """Получение режима этикетки"""
    
    return {
        DeliveryType.AVITO : LabelMode.BARCODE,
        DeliveryType.CDEK : LabelMode.BARCODE,
        DeliveryType.DPD : LabelMode.BARCODE,
        DeliveryType.POST_RU : LabelMode.BARCODE,
        DeliveryType.FIVE_POST : LabelMode.QR,
    }.get(delivery)