# -*- coding: utf-8 -*-
"""frontend/helpers.py — Shared dialog and snackbar utilities."""

import flet as ft
from frontend import theme as t


def show_snack(page: ft.Page, msg: str, color: str = t.TEXT_DIM):
    """Show a SnackBar in Flet 0.80+."""
    sb = ft.SnackBar(
        content=ft.Text(msg, color=t.TEXT),
        bgcolor=t.SURFACE2,
    )
    page.snack_bar = sb
    sb.open = True
    page.update()


def open_dialog(page: ft.Page, dlg: ft.AlertDialog):
    """Open an AlertDialog in Flet 0.80+."""
    page.dialog = dlg
    dlg.open = True
    page.update()


def close_dialog(page: ft.Page, dlg: ft.AlertDialog):
    """Close an AlertDialog in Flet 0.80+."""
    dlg.open = False
    page.update()
