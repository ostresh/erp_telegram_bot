from .full_finance_report import router as full_finance_report_router
from .product import PRODUCT_REPORT_ROUTERS

REPORTS_ROUTERS = [
    full_finance_report_router,
    *PRODUCT_REPORT_ROUTERS
]

__all__ = [
    'REPORTS_ROUTERS'
]