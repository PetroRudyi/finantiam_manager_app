# backend/__init__.py
from backend.models import Receipt, InvoiceItem, AppSettings
from backend.storage import (
    load_receipts, save_receipts, add_receipt, update_receipt,
    delete_receipts, update_receipts_date,
    load_settings, save_settings,
    filter_receipts_by_period, get_monthly_totals,
    get_category_totals, get_summary, export_to_csv,
    recalculate_all_receipts,
)
from backend.exchange_service import (
    get_rate, get_rate_for_receipt, convert_amount,
)
from backend.ai_service import extract_receipt_from_image, merge_duplicate_items
from backend.config import (
    CURRENCIES, CURRENCY_CODES, CURRENCY_MAP, DEFAULT_CURRENCY,
    DEFAULT_CATEGORIES, DEFAULT_CATEGORY, get_symbol, normalize_currency,
)
