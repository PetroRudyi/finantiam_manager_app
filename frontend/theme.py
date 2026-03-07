# -*- coding: utf-8 -*-
"""
frontend/theme.py
Color palette and reusable UI constants.
Compatible with Flet >= 0.80.0

Key changes vs old API:
- ft.padding.only()     → ft.Padding(left=..., right=..., top=..., bottom=...)
- ft.padding.symmetric()→ ft.Padding(left=h, right=h, top=v, bottom=v)
- ft.margin.only()      → ft.Margin(left=..., right=..., top=..., bottom=...)
- ft.border.all()       → ft.Border(left=s, right=s, top=s, bottom=s)  where s=ft.BorderSide
- ft.border.only()      → ft.Border(top=ft.BorderSide(...)) etc.
- ft.border_radius.only()→ ft.BorderRadius(tl, tr, br, bl)
- ft.Text(letter_spacing=)  NOT supported as kwarg — use ft.TextStyle inside style
- ft.app()              → ft.run()
"""

import flet as ft

from backend.config import get_symbol, DEFAULT_CURRENCY


# ──────────────────────────────────────────
#  Ukrainian locale helpers
# ──────────────────────────────────────────

UA_MONTHS_SHORT = {
    1: "Січ.", 2: "Лют.", 3: "Бер.", 4: "Квіт.", 5: "Трав.", 6: "Черв.",
    7: "Лип.", 8: "Серп.", 9: "Вер.", 10: "Жовт.", 11: "Лист.", 12: "Груд.",
}

UA_DAYS_SHORT = {
    0: "Пн", 1: "Вт", 2: "Ср", 3: "Чт", 4: "Пт", 5: "Сб", 6: "Нд",
}

UA_MONTHS_CHART = {
    1: "Сі", 2: "Лю", 3: "Бе", 4: "Кв", 5: "Тр", 6: "Чр",
    7: "Лп", 8: "Сп", 9: "Ве", 10: "Жо", 11: "Лс", 12: "Гр",
}


def alpha(color: str, a: str) -> str:
    """Add alpha to hex color. Flet uses #AARRGGBB format."""
    return f"#{a}{color[1:]}"


def format_amount(val: float, sign: bool = False, currency: str = DEFAULT_CURRENCY) -> str:
    """Format amount: space thousands, omit .00 decimals, use currency symbol."""
    abs_val = abs(val)
    if abs_val == int(abs_val):
        s = f"{int(abs_val):,}".replace(",", " ")
    else:
        s = f"{abs_val:,.2f}".replace(",", " ")
    prefix = ""
    if sign:
        prefix = "+" if val > 0 else "−" if val < 0 else ""
    symbol = get_symbol(currency)
    return f"{prefix}{symbol}{s}"


# ──────────────────────────────────────────
#  Palette
# ──────────────────────────────────────────
BG          = "#0e0e10"
SURFACE     = "#18181c"
SURFACE2    = "#222228"
BORDER      = "#2a2a32"
TEXT        = "#f0f0f4"
TEXT_DIM    = "#7a7a88"
TEXT_DIMMER = "#44444e"
RED         = "#ff4d5a"
BLUE        = "#3d9bff"
GREEN       = "#3dcc8e"
AMBER       = "#ffb240"
ACCENT      = "#7c6aff"
WHITE       = "#ffffff"

CATEGORY_COLORS = [
    "#ff4d5a", "#ffb240", "#7c6aff", "#3d9bff",
    "#3dcc8e", "#e5a35a", "#a8d5a2",
]


# ──────────────────────────────────────────
#  Padding / Margin helpers (Flet 0.80+)
# ──────────────────────────────────────────

def pad(left=0, right=0, top=0, bottom=0) -> ft.Padding:
    return ft.Padding(left=left, right=right, top=top, bottom=bottom)


def pad_sym(horizontal=0, vertical=0) -> ft.Padding:
    return ft.Padding(left=horizontal, right=horizontal, top=vertical, bottom=vertical)


def pad_only(left=0, right=0, top=0, bottom=0) -> ft.Padding:
    return ft.Padding(left=left, right=right, top=top, bottom=bottom)


def mar(left=0, right=0, top=0, bottom=0) -> ft.Margin:
    return ft.Margin(left=left, right=right, top=top, bottom=bottom)


def mar_only(left=0, right=0, top=0, bottom=0) -> ft.Margin:
    return ft.Margin(left=left, right=right, top=top, bottom=bottom)


def border_all(width=1, color=BORDER) -> ft.Border:
    s = ft.BorderSide(width, color)
    return ft.Border(left=s, right=s, top=s, bottom=s)


def border_top(width=1, color=BORDER) -> ft.Border:
    return ft.Border(top=ft.BorderSide(width, color))


def border_bottom(width=1, color=BORDER) -> ft.Border:
    return ft.Border(bottom=ft.BorderSide(width, color))


# ──────────────────────────────────────────
#  Text helpers  (letter_spacing NOT a Text kwarg in 0.80+)
# ──────────────────────────────────────────

def mono_label(text: str, size=9, color=TEXT_DIMMER) -> ft.Text:
    """Uppercase monospace label (replaces letter_spacing on Text)."""
    return ft.Text(
        text.upper(),
        size=size,
        color=color,
        font_family="monospace",
        style=ft.TextStyle(letter_spacing=1.2),
    )


def section_title(text: str) -> ft.Container:
    return ft.Container(
        content=mono_label(text),
        padding=pad_only(left=18, right=18, top=12, bottom=6),
    )


def divider() -> ft.Divider:
    return ft.Divider(height=1, color=BORDER, thickness=1)


# ──────────────────────────────────────────
#  Common text_field factory
# ──────────────────────────────────────────

def text_field(label_text: str, value="", hint="", on_change=None,
               expand=True, password=False) -> ft.TextField:
    tf = ft.TextField(
        label=label_text,
        value=value,
        hint_text=hint,
        password=password,
        expand=expand,
        bgcolor=SURFACE2,
        border_color=BORDER,
        focused_border_color=ACCENT,
        label_style=ft.TextStyle(size=9, color=TEXT_DIMMER, font_family="monospace"),
        text_style=ft.TextStyle(size=13, color=TEXT),
        hint_style=ft.TextStyle(size=12, color=TEXT_DIMMER),
        border_radius=9,
        content_padding=pad_sym(horizontal=12, vertical=9),
    )
    if on_change:
        tf.on_change = on_change
    return tf
