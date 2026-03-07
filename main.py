# -*- coding: utf-8 -*-
"""
main.py  —  Expense Tracker entry point
Compatible with Flet >= 0.80.0

Run:  python main.py
"""

import flet as ft

from app.state import AppState
from app.shell import AppShell


def main(page: ft.Page):
    state = AppState()
    shell = AppShell(page, state)
    shell.start()


if __name__ == "__main__":
    ft.run(main)
