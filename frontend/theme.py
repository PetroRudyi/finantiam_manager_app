# -*- coding: utf-8 -*-
"""
frontend/theme.py
Color palette and reusable UI constants.
Compatible with Flet >= 0.80.0

Key changes vs old API:
- ft.padding.only()     -> ft.Padding(left=..., right=..., top=..., bottom=...)
- ft.padding.symmetric()-> ft.Padding(left=h, right=h, top=v, bottom=v)
- ft.margin.only()      -> ft.Margin(left=..., right=..., top=..., bottom=...)
- ft.border.all()       -> ft.Border(left=side, right=side, top=side, bottom=side)
- ft.border.only()      -> ft.Border(top=ft.BorderSide(...)) etc.
- ft.border_radius.only()-> ft.BorderRadius(tl, tr, br, bl)
- ft.Text(letter_spacing=)  NOT supported as kwarg -- use ft.TextStyle inside style
- ft.app()              -> ft.run()
"""

import flet as ft

from backend.config import get_symbol, DEFAULT_CURRENCY, BASE_WIDTH, BASE_HEIGHT
from frontend.sizes import (
    FONT_SM, FONT_BODY, FONT_LG, LETTER_SPACING,
    PAD_PAGE_H, PAD_SECTION_TOP, PAD_SECTION_BOTTOM,
    FIELD_RADIUS, FIELD_PAD_H, FIELD_PAD_V,
    BORDER_WIDTH, DIVIDER_H,
)


# ──────────────────────────────────────────
#  Locale helpers (loaded from translations)
# ──────────────────────────────────────────

def get_months_short() -> dict:
    from frontend.localisation import t
    return {i: t(f"months_short.{i}") for i in range(1, 13)}


def get_days_short() -> dict:
    from frontend.localisation import t
    return {i: t(f"days_short.{i}") for i in range(7)}


def get_days_full() -> dict:
    from frontend.localisation import t
    return {i: t(f"days_full.{i}") for i in range(7)}


def get_months_chart() -> dict:
    from frontend.localisation import t
    return {i: t(f"months_chart.{i}") for i in range(1, 13)}


# ──────────────────────────────────────────
#  Scaling utility
# ──────────────────────────────────────────

_scale_factor: float = 1.0


def init_scale(page_width: float, page_height: float):
    """Calculate scale factor based on actual screen size vs base resolution.

    Must be called AFTER page.update() so that page.width / page.height
    reflect the real viewport dimensions (especially on mobile).
    """
    global _scale_factor
    if page_width > 0 and page_height > 0:
        _scale_factor = min(page_width / BASE_WIDTH, page_height / BASE_HEIGHT)


def scaled(value: float) -> float:
    """Scale a design-time pixel value to match the current screen density.

    Usage:  scaled(18)  — returns 18 on the base 390x720 design,
            ~50 on a Pixel 7 (1080x2400), etc.
    """
    return round(value * _scale_factor)


def alpha(color: str, a: str) -> str:
    """Add alpha to hex color. Flet uses #AARRGGBB format."""
    return f"#{a}{color[1:]}"


def format_amount(val: float, sign: bool = False, currency: str = DEFAULT_CURRENCY) -> str:
    """Format amount: space thousands, omit .00 decimals, use currency symbol."""
    abs_val = abs(val)
    if abs_val == int(abs_val):
        formatted = f"{int(abs_val):,}".replace(",", " ")
    else:
        formatted = f"{abs_val:,.2f}".replace(",", " ")
    prefix = ""
    if sign:
        prefix = "+" if val > 0 else "\u2212" if val < 0 else ""
    symbol = get_symbol(currency)
    return f"{prefix}{symbol}{formatted}"


# ──────────────────────────────────────────
#  Palette
# ──────────────────────────────────────────
BG          = "#0e0e10"
SURFACE     = "#18181c"
SURFACE2    = "#222228"
BORDER      = "#2a2a32"
TEXT        = "#f0f0f4"
TEXT_DIM    = "#7a7a88"
TEXT_DIMMER = "#9898a4"
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


def border_all(width=scaled(BORDER_WIDTH), color=BORDER) -> ft.Border:
    side = ft.BorderSide(width, color)
    return ft.Border(left=side, right=side, top=side, bottom=side)


def border_top(width=scaled(BORDER_WIDTH), color=BORDER) -> ft.Border:
    return ft.Border(top=ft.BorderSide(width, color))


def border_bottom(width=scaled(BORDER_WIDTH), color=BORDER) -> ft.Border:
    return ft.Border(bottom=ft.BorderSide(width, color))


# ──────────────────────────────────────────
#  Text helpers  (letter_spacing NOT a Text kwarg in 0.80+)
# ──────────────────────────────────────────

def mono_label(text: str, size=None, color=TEXT_DIMMER) -> ft.Text:
    """Uppercase monospace label (replaces letter_spacing on Text)."""
    return ft.Text(
        text.upper(),
        size=size if size is not None else scaled(FONT_SM),
        color=color,
        font_family="monospace",
        style=ft.TextStyle(letter_spacing=scaled(LETTER_SPACING)),
    )


def section_title(text: str) -> ft.Container:
    return ft.Container(
        content=mono_label(text),
        padding=pad_only(left=int(scaled(PAD_PAGE_H)), right=int(scaled(PAD_PAGE_H)),
                         top=int(scaled(PAD_SECTION_TOP)), bottom=int(scaled(PAD_SECTION_BOTTOM))),
    )


def divider() -> ft.Divider:
    return ft.Divider(height=scaled(DIVIDER_H), color=BORDER, thickness=scaled(DIVIDER_H))


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
        label_style=ft.TextStyle(size=scaled(FONT_SM), color=TEXT_DIMMER, font_family="monospace"),
        text_style=ft.TextStyle(size=scaled(FONT_LG), color=TEXT),
        hint_style=ft.TextStyle(size=scaled(FONT_BODY), color=TEXT_DIMMER),
        border_radius=scaled(FIELD_RADIUS),
        content_padding=pad_sym(horizontal=int(scaled(FIELD_PAD_H)), vertical=int(scaled(FIELD_PAD_V))),
    )
    if on_change:
        tf.on_change = on_change
    return tf
