from .full_finance_report.dialog import full_finance_report_dialog
from .product.dialog import product_report_dialog

REPORTS_DIALOGS = [
    full_finance_report_dialog,
    product_report_dialog
]

__all__ = [
    'REPORTS_DIALOGS'
]