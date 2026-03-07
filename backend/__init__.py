# backend/__init__.py

# Models
from backend.models import Receipt, InvoiceItem, AppSettings

# Storage
from backend.storage import (
    load_receipts, save_receipts, add_receipt, update_receipt,
    delete_receipts, update_receipts_date,
    load_settings, save_settings,
    export_to_csv, recalculate_all_receipts,
)

# Analytics
from backend.analytics import (
    filter_receipts_by_period, get_monthly_totals,
    get_category_totals, get_summary,
)

# Exchange
from backend.exchange_service import (
    get_rate, get_rate_for_receipt, convert_amount,
)

# AI
from backend.ai_service import extract_receipt_from_image, merge_duplicate_items

# Config
from backend.config import (
    CURRENCIES, CURRENCY_CODES, CURRENCY_MAP, DEFAULT_CURRENCY,
    DEFAULT_CATEGORIES, DEFAULT_CATEGORY, get_symbol, normalize_currency,
    APP_VERSION,
)

# Update
from backend.update_service import check_for_update, get_apk_url
