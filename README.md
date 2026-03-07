# Expense Tracker

A minimalist app for tracking expenses and income.
Built with [Flet](https://flet.dev/) >= 0.80.0 (Python).

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run
python main.py
```

---

## Project Structure

```
expense_tracker/
├── main.py                        # Entry point
├── requirements.txt
├── README.md
├── backend/
│   ├── __init__.py
│   ├── models.py                  # Pydantic: Receipt, InvoiceItem, AppSettings
│   ├── storage.py                 # JSON/CSV storage
│   └── ai_service.py             # Gemini AI receipt recognition
├── frontend/
│   ├── __init__.py
│   ├── theme.py                   # Colors, padding/border helpers (Flet 0.80+)
│   ├── screen_transactions.py    # Screen 01
│   ├── screen_add_receipt.py     # Screen 02
│   ├── screen_dashboard.py       # Screen 03
│   └── screen_settings.py        # Screen 04
└── data/
    ├── receipts.json
    ├── settings.json
    └── export.csv                 # Generated on export
```

---

## Flet 0.80+ Compatibility

This version fixes all deprecation warnings:

| Old API (pre-0.80) | New API (0.80+) |
|---|---|
| `ft.app(target=main)` | `ft.run(target=main)` |
| `ft.padding.only(...)` | `ft.Padding(left=..., right=..., top=..., bottom=...)` |
| `ft.padding.symmetric(...)` | `ft.Padding(left=h, right=h, top=v, bottom=v)` |
| `ft.margin.only(...)` | `ft.Margin(left=..., right=..., ...)` |
| `ft.border.all(w, c)` | `ft.Border(left=ft.BorderSide(w,c), right=..., top=..., bottom=...)` |
| `ft.border.only(top=...)` | `ft.Border(top=ft.BorderSide(w, c))` |
| `ft.border_radius.only(...)` | `ft.BorderRadius(tl, tr, br, bl)` |
| `ft.Text(letter_spacing=...)` | `ft.Text(style=ft.TextStyle(letter_spacing=...))` |

---

## AI Receipt Recognition

1. Get an API key: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Paste it in **Settings → Gemini API Key**
3. In the receipt form, click **Upload Receipt Photo (AI)**
4. All fields will be filled in automatically

---

## Requirements

- Python 3.10+
- Flet 0.80+
