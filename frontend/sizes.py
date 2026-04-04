# -*- coding: utf-8 -*-
"""
frontend/sizes.py
Global UI size constants shared across all screens.

All values are in design pixels (base resolution 390x720).
Use with scaled() for responsive rendering:
    from frontend.sizes import FONT_LG, PAD_PAGE_H
    ft.Text("Hello", size=scaled(FONT_LG))

To change a size globally, edit this file.
For screen-specific sizes, see frontend/screens/<screen>/sizes.py.
"""

# ── Шрифти (Font sizes) ──────────────────────────────
FONT_TAB    = 11    # Нижнє меню (tab bar)
FONT_TAB_PERIOD = 13  # Вкладки періоду (Daily/Weekly/Total)
FONT_XS     = 13    # Найменший: заголовки колонок таблиці, мітки графіків
FONT_SM     = 13   # Малий: секційні заголовки, моно-мітки, підписи
FONT_SM_MD  = 10   # Перемикачі, помилки, статусний текст
FONT_MD     = 11   # Вкладки, посилання, кнопки з текстом
FONT_BODY   = 12   # Основний текст: поля, підказки, налаштування
FONT_LG     = 14   # Великий текст: назви у списках, значення полів
FONT_NAV       = 14   # Навігаційні елементи: назва місяця
FONT_NAV_ARROW = 22   # Стрілки навігації місяця
FONT_TITLE  = 15   # Великі елементи UI (drag handle тощо)
FONT_HEADER = 18   # Заголовки екранів та діалогів

# ── Шрифти діалогових вікон (Dialog font sizes) ─────
FONT_DIALOG_TITLE  = 16   # Заголовок діалогового вікна
FONT_DIALOG_BODY   = 14   # Основний текст діалогового вікна
FONT_DIALOG_ACTION = 14   # Кнопки дій діалогового вікна

# ── Міжлітерний інтервал ──────────────────────────────
LETTER_SPACING = 1.2   # Інтервал для моно-міток (UPPER CASE)

# ── Відступи сторінки ─────────────────────────────────
PAD_PAGE_H        = 18   # Горизонтальний відступ від краю екрану
PAD_SECTION_TOP   = 12   # Верхній відступ заголовка секції
PAD_SECTION_BOTTOM = 6   # Нижній відступ заголовка секції
PAD_HEADER_TOP    = 5    # Верхній відступ заголовка екрану
PAD_HEADER_BOTTOM = 10   # Нижній відступ заголовка екрану

# ── Поля вводу ────────────────────────────────────────
FIELD_RADIUS  = 9    # Радіус скруглення полів вводу
FIELD_PAD_H   = 12   # Горизонтальний внутрішній відступ поля
FIELD_PAD_V   = 9    # Вертикальний внутрішній відступ поля

# ── Кнопки ────────────────────────────────────────────
BTN_RADIUS    = 9    # Радіус скруглення кнопок
BTN_PAD_H     = 18   # Горизонтальний відступ всередині кнопки
BTN_PAD_V     = 10   # Вертикальний відступ всередині кнопки

# ── Проміжки (Spacing) ───────────────────────────────
GAP_XS   = 2    # Мінімальний проміжок
GAP_SM   = 4    # Малий проміжок
GAP_MD   = 6    # Середній проміжок
GAP_LG   = 8    # Великий проміжок
GAP_XL   = 10   # Найбільший проміжок

# ── Базові розміри елементів ──────────────────────────
BORDER_WIDTH  = 1    # Стандартна ширина обводки
DIVIDER_H     = 1    # Висота розділювача

# ── Малі кнопки-іконки (edit/delete) ─────────────────
ICON_BTN_SM      = 18   # Розмір кнопки-іконки (ширина і висота)
ICON_BTN_RADIUS  = 4    # Радіус скруглення кнопки-іконки
