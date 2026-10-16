from .movement_report import router as movement_report_router
from .sales_report import router as sales_report_router

PRODUCT_REPORT_ROUTERS = [
    movement_report_router,
    sales_report_router
]

__all__ = [
    'PRODUCT_REPORT_ROUTERS'
]