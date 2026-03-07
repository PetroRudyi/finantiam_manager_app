# -*- coding: utf-8 -*-
"""backend/exchange_service.py — Currency exchange rates.

Sources:
1. Frankfurter API (.app / .dev) — ECB rates, historical (no UAH)
2. ECB XML feed (hist-90d) — fallback for last 90 days (no UAH)
3. NBU API (bank.gov.ua) — for UAH conversions
"""

import datetime
import json
import xml.etree.ElementTree as ET
from typing import Optional, Dict

import httpx

from backend.storage._paths import DATA_DIR

RATES_CACHE_FILE = DATA_DIR / "exchange_rates.json"
API_TIMEOUT = 10  # seconds

FRANKFURTER_URLS = [
    "https://api.frankfurter.app",
    "https://api.frankfurter.dev",
]
ECB_HIST90_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml"
NBU_API_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"


# ── Cache ─────────────────────────────────────────────────────

def _load_cache() -> dict:
    if RATES_CACHE_FILE.exists():
        try:
            return json.loads(RATES_CACHE_FILE.read_text("utf-8"))
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict):
    DATA_DIR.mkdir(exist_ok=True)
    RATES_CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), "utf-8"
    )


# ── NBU API (for UAH) ────────────────────────────────────────

def _fetch_nbu_rates(target_date: datetime.date) -> Optional[Dict[str, float]]:
    """Fetch rates from NBU.  Returns {currency_code: uah_per_unit}."""
    date_str = target_date.strftime("%Y%m%d")
    url = f"{NBU_API_URL}?date={date_str}&json"
    try:
        resp = httpx.get(url, timeout=API_TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
        data = resp.json()
        rates: Dict[str, float] = {}
        for item in data:
            cc = item.get("cc")
            rate = item.get("rate")
            if cc and rate:
                rates[cc] = float(rate)
        return rates if rates else None
    except Exception as exc:
        print(f"[exchange] NBU API error: {exc}")
        return None


def _get_rate_via_nbu(
    from_currency: str, to_currency: str, date: datetime.date
) -> Optional[float]:
    """Get exchange rate when UAH is involved.

    NBU rates are in format: 1 foreign unit = X UAH.
    """
    nbu_rates = _fetch_nbu_rates(date)
    if not nbu_rates:
        return None

    if from_currency == "UAH" and to_currency == "UAH":
        return 1.0

    if from_currency == "UAH":
        # UAH → X:  need 1/nbu_rate[X]
        if to_currency in nbu_rates:
            return round(1.0 / nbu_rates[to_currency], 6)
        return None

    if to_currency == "UAH":
        # X → UAH:  need nbu_rate[X]
        if from_currency in nbu_rates:
            return round(nbu_rates[from_currency], 6)
        return None

    # Both non-UAH but we're called because one of them isn't in ECB
    # Cross-rate through UAH:  from → UAH → to
    if from_currency in nbu_rates and to_currency in nbu_rates:
        return round(nbu_rates[from_currency] / nbu_rates[to_currency], 6)
    return None


# ── Frankfurter API ──────────────────────────────────────────

def _fetch_rates_frankfurter(
    base_currency: str, date: datetime.date
) -> Optional[Dict[str, float]]:
    """Try both Frankfurter endpoints (.app and .dev)."""
    date_str = date.isoformat()
    for base_url in FRANKFURTER_URLS:
        url = f"{base_url}/{date_str}?from={base_currency}"
        try:
            resp = httpx.get(url, timeout=API_TIMEOUT, follow_redirects=True)
            resp.raise_for_status()
            data = resp.json()
            rates = data.get("rates")
            if rates:
                return rates
        except Exception as exc:
            print(f"[exchange] Frankfurter ({base_url}) error: {exc}")
            continue
    return None


# ── ECB XML feed ─────────────────────────────────────────────

def _parse_ecb_xml(xml_text: str) -> Dict[str, Dict[str, float]]:
    """Parse ECB XML → {date_str: {currency: eur_rate}}."""
    ns = {"eurofxref": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"}
    root = ET.fromstring(xml_text)
    result: Dict[str, Dict[str, float]] = {}
    for cube in root.findall(".//eurofxref:Cube/eurofxref:Cube", ns):
        time = cube.get("time")
        if not time:
            continue
        day_rates: Dict[str, float] = {}
        for rate_cube in cube:
            currency = rate_cube.get("currency")
            rate_val = rate_cube.get("rate")
            if currency and rate_val:
                day_rates[currency] = float(rate_val)
        if day_rates:
            result[time] = day_rates
    return result


def _eur_rates_to_base(
    eur_rates: Dict[str, float], base_currency: str
) -> Optional[Dict[str, float]]:
    """Convert EUR-based rates to base_currency-based rates."""
    if base_currency == "EUR":
        return dict(eur_rates)
    if base_currency not in eur_rates:
        return None
    base_in_eur = eur_rates[base_currency]
    rates: Dict[str, float] = {"EUR": round(1.0 / base_in_eur, 6)}
    for cur, eur_rate in eur_rates.items():
        if cur != base_currency:
            rates[cur] = round(eur_rate / base_in_eur, 6)
    return rates


def _fetch_ecb_rates(
    base_currency: str, target_date: datetime.date
) -> Optional[Dict[str, float]]:
    """Fetch rates from ECB hist-90d XML."""
    try:
        resp = httpx.get(ECB_HIST90_URL, timeout=15, follow_redirects=True)
        resp.raise_for_status()
        all_rates = _parse_ecb_xml(resp.text)

        date_str = target_date.isoformat()
        # Try exact date
        if date_str in all_rates:
            return _eur_rates_to_base(all_rates[date_str], base_currency)

        # Try nearest earlier date (weekends / holidays)
        for delta in range(1, 5):
            fallback = (target_date - datetime.timedelta(days=delta)).isoformat()
            if fallback in all_rates:
                return _eur_rates_to_base(all_rates[fallback], base_currency)

        # Return the most recent available
        if all_rates:
            latest = max(all_rates.keys())
            print(f"[exchange] ECB: exact date {date_str} not found, using {latest}")
            return _eur_rates_to_base(all_rates[latest], base_currency)

        return None
    except Exception as exc:
        print(f"[exchange] ECB hist-90d error: {exc}")
        return None


# ── Public API ────────────────────────────────────────────────

# Currencies NOT in ECB/Frankfurter that need special handling
_NON_ECB_CURRENCIES = {"UAH"}


def get_rate(
    from_currency: str,
    to_currency: str,
    date: datetime.date,
) -> Optional[float]:
    """Get the exchange rate to convert from `from_currency` to `to_currency`
    on the given date.

    Returns the rate (float) or None if unavailable.
    """
    if from_currency == to_currency:
        return 1.0

    cache = _load_cache()
    date_str = date.isoformat()

    # Check cache
    cached = cache.get(date_str, {}).get(from_currency, {}).get(to_currency)
    if cached is not None:
        print(f"[exchange] {from_currency}→{to_currency} {date_str}: {cached} (cache)")
        return cached

    rate = None
    source = ""

    # UAH not in ECB — use NBU (National Bank of Ukraine)
    if from_currency in _NON_ECB_CURRENCIES or to_currency in _NON_ECB_CURRENCIES:
        rate = _get_rate_via_nbu(from_currency, to_currency, date)
        if rate is not None:
            source = "NBU"
    else:
        # 1) Try Frankfurter API
        rates = _fetch_rates_frankfurter(from_currency, date)
        if rates and to_currency in rates:
            cache.setdefault(date_str, {}).setdefault(from_currency, {}).update(rates)
            _save_cache(cache)
            r = rates[to_currency]
            print(f"[exchange] {from_currency}→{to_currency} {date_str}: {r} (Frankfurter)")
            return r

        # 2) Fallback: ECB XML feed
        rates = _fetch_ecb_rates(from_currency, date)
        if rates and to_currency in rates:
            cache.setdefault(date_str, {}).setdefault(from_currency, {}).update(rates)
            _save_cache(cache)
            r = rates[to_currency]
            print(f"[exchange] {from_currency}→{to_currency} {date_str}: {r} (ECB XML)")
            return r

    # Cache the single rate if found
    if rate is not None:
        cache.setdefault(date_str, {}).setdefault(from_currency, {})[to_currency] = rate
        _save_cache(cache)
        print(f"[exchange] {from_currency}→{to_currency} {date_str}: {rate} ({source})")
        return rate

    # 3) Fallback: search nearby dates in cache
    for delta in range(1, 6):
        fallback_date = (date - datetime.timedelta(days=delta)).isoformat()
        cached = cache.get(fallback_date, {}).get(from_currency, {}).get(to_currency)
        if cached is not None:
            print(f"[exchange] {from_currency}→{to_currency} {date_str}: {cached} (cache fallback {fallback_date})")
            return cached

    print(f"[exchange] FAIL {from_currency}→{to_currency} {date_str}: no rate found")
    return None


def get_rate_for_receipt(
    receipt_currency: str,
    base_currency: str,
    receipt_date: datetime.datetime,
) -> Optional[float]:
    """Convenience wrapper: get rate for a receipt using its date."""
    return get_rate(receipt_currency, base_currency, receipt_date.date())


def convert_amount(amount: float, rate: Optional[float]) -> Optional[float]:
    """Multiply amount by rate. Returns None if rate is None."""
    if rate is None:
        return None
    return round(amount * rate, 2)
