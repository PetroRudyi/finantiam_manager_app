# Expense Tracker

Мінімалістичний застосунок для обліку витрат і надходжень.
Побудований на [Flet](https://flet.dev/) >= 0.80.0 (Python).

---

## Швидкий старт

```bash
# 1. Встанови залежності
pip install -r requirements.txt

# 2. Запусти
python main.py
```

---

## Структура проекту

```
expense_tracker/
├── main.py                        # Точка входу
├── requirements.txt
├── README.md
├── backend/
│   ├── __init__.py
│   ├── models.py                  # Pydantic: Receipt, InvoiceItem, AppSettings
│   ├── storage.py                 # JSON/CSV зберігання
│   └── ai_service.py             # Gemini AI розпізнавання чеків
├── frontend/
│   ├── __init__.py
│   ├── theme.py                   # Кольори, padding/border хелпери (Flet 0.80+)
│   ├── screen_transactions.py    # Екран 01
│   ├── screen_add_receipt.py     # Екран 02
│   ├── screen_dashboard.py       # Екран 03
│   └── screen_settings.py        # Екран 04
└── data/
    ├── receipts.json
    ├── settings.json
    └── export.csv                 # генерується при вигрузці
```

---

## Сумісність з Flet 0.80+

Ця версія виправляє всі deprecation warnings:

| Старий API (до 0.80) | Новий API (0.80+) |
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

## AI розпізнавання чеків

1. Отримай ключ: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Встав у **Налаштування → API ключ Gemini**
3. У формі чеку натисни **Завантажити фото чеку (AI)**
4. Усі поля заповняться автоматично

---

## Вимоги

- Python 3.10+
- Flet 0.80+
