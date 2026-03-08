# -*- coding: utf-8 -*-
"""AI receipt photo scanning handler."""

import threading
import difflib
from typing import List

import flet as ft

import backend
from backend.models import InvoiceItem
from backend.config import DEFAULT_CATEGORY
from frontend.helpers import show_snack
from frontend.localisation import t as tr


async def pick_ai_image(screen, page: ft.Page):
    """Handle AI receipt photo selection and processing."""
    settings = screen.app_state.settings
    if not settings.gemini_api_key:
        show_snack(page, tr("ai.no_api_key"))
        return
    if screen._ai_running:
        return

    files = await ft.FilePicker().pick_files(
        dialog_title=tr("ai.pick_photo"),
        allowed_extensions=["jpg", "jpeg", "png", "gif"],
        allow_multiple=False,
        file_type=ft.FilePickerFileType.CUSTOM,
    )
    if not files:
        return

    path = files[0].path
    if not path:
        show_snack(page, tr("ai.no_file_path"))
        return

    screen._ai_running = True
    try:
        screen._form.ai_btn.on_click = None
        screen._form.ai_btn.ink = False
        screen._form.ai_btn.update()
    except Exception:
        pass
    _set_ai_status(screen, tr("ai.status_photo"))

    def run():
        try:
            _set_ai_status(screen, tr("ai.status_gemini"))
            data = backend.extract_receipt_from_image(
                image_path=path,
                api_key=settings.gemini_api_key,
                default_currency=settings.default_currency,
                categories=settings.categories,
            )
            _set_ai_status(screen, tr("ai.status_response"))
            merged = backend.merge_duplicate_items(data.invoice_items)
            screen._business = data.business_name or ""
            screen._currency = data.currency
            if data.created_date:
                screen._date = data.created_date

            _set_ai_status(screen, tr("ai.status_categories"))
            screen._items = [
                InvoiceItem(
                    name=i.name,
                    quantity=i.quantity,
                    price=i.price,
                    category=_map_category(i.category, settings, screen.app_state),
                )
                for i in merged
            ]
            _set_ai_status(screen, tr("ai.status_form"))

            screen._ai_running = False
            screen._ai_status_text = tr("ai.status_done").replace("{count}", str(len(screen._items)))
            screen._build()
            try:
                screen.update()
            except Exception:
                pass
            try:
                page.update()
            except Exception:
                pass
        except Exception:
            screen._ai_running = False
            _set_ai_status(screen, tr("ai.status_error"))
            try:
                from frontend.screens.add_receipt.ai_handler import get_ai_click_handler

                screen._form.ai_btn.on_click = (
                    get_ai_click_handler(screen, page)
                    if bool(settings.gemini_api_key)
                    else None
                )
                screen._form.ai_btn.ink = bool(settings.gemini_api_key)
                screen._form.ai_btn.update()
            except Exception:
                pass

    try:
        page.run_thread(run)
    except Exception:
        threading.Thread(target=run, daemon=True).start()


def get_ai_click_handler(screen, page: ft.Page):
    async def _handler(e):
        await pick_ai_image(screen, page)

    return _handler


def _set_ai_status(screen, text: str):
    screen._ai_status_text = text
    try:
        screen._form.ai_status.value = text
        screen._form.ai_status.update()
    except Exception:
        try:
            screen.page.update()
        except Exception:
            pass


def _map_category(name: str, settings, app_state) -> str:
    raw = (name or "").strip()
    if not raw:
        return settings.ensure_category(DEFAULT_CATEGORY)

    cid = settings.get_category_id_by_name(raw)
    if cid is None:
        for c in settings.categories:
            if not c.deleted and c.name.strip().lower() == raw.lower():
                cid = c.id
                break

    if cid is None:
        active_names = [c.name for c in settings.categories
                        if not c.deleted and c.name.strip()]
        match = difflib.get_close_matches(raw, active_names, n=1, cutoff=0.82)
        if match:
            cid = settings.get_category_id_by_name(match[0])

    if cid is None:
        cid = settings.ensure_category(raw)
        backend.save_settings(settings)
        app_state.settings = settings
    return cid
