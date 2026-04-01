# -*- coding: utf-8 -*-
"""Category management sub-screen.

Uses ft.ReorderableListView for REAL-TIME animated reordering.

Requirements:
- flet>=0.80.0
"""

import flet as ft

import backend
from backend.models import AppSettings, Category
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import (
    FONT_SM, FONT_SM_MD, FONT_BODY, FONT_LG, FONT_NAV,
    PAD_PAGE_H, BTN_PAD_V, GAP_LG, BORDER_WIDTH,
)
from frontend.screens.settings.sizes import (
    CAT_DRAG_HANDLE, CAT_DRAG_PAD_H, CAT_DRAG_PAD_V, CAT_EDIT_RADIUS, CAT_EDIT_PAD_H, CAT_EDIT_PAD_V,
    CAT_ROW_PAD_V, CAT_EDIT_FIELD_RADIUS, CAT_EDIT_FIELD_PAD_V,
    CAT_ADD_BTN_PAD_H, CAT_ADD_BTN_PAD_V, CAT_HINT_PAD_BOTTOM,
    DD_PAD_H,
)


class CategoryEditor:
    """Manages category list CRUD within the settings screen."""

    def __init__(self, app_state, on_rebuild):
        self.app_state = app_state
        self._on_rebuild = on_rebuild
        self._editing_cat_idx = None

        self._new_cat_field = None
        self._cat_error = None
        self._list = None
        self._edit_cat_field = None
        self._scroll_col = None

    def build(self) -> ft.Column:
        settings: AppSettings = self.app_state.settings

        self._new_cat_field = ft.TextField(
            hint_text=tr("category_editor.new_category_hint"),
            bgcolor=t.SURFACE2,
            border_color=t.BORDER,
            focused_border_color=t.ACCENT,
            border_radius=scaled(8),
            expand=True,
            text_style=ft.TextStyle(size=scaled(FONT_BODY), color=t.TEXT),
            hint_style=ft.TextStyle(size=scaled(FONT_BODY), color=t.TEXT_DIMMER),
            content_padding=t.pad_sym(horizontal=scaled(DD_PAD_H), vertical=scaled(CAT_ADD_BTN_PAD_V)),
            key="new_cat_field",
            on_focus=lambda e: self._scroll_to("new_cat_field"),
        )

        self._cat_error = ft.Text("", size=scaled(FONT_SM_MD), color=t.RED)

        # REAL animated reorder list
        self._list = ft.ReorderableListView(
            expand=True,
            # IMPORTANT: we'll provide our own drag start area (the whole row)
            show_default_drag_handles=False,
            on_reorder=lambda e: self._handle_reorder(e, settings),
            controls=[],
        )

        self._refresh_list(settings)

        active_cats = [c for c in settings.categories if not c.deleted]
        editing_label = ""
        if self._editing_cat_idx is not None and 0 <= self._editing_cat_idx < len(active_cats):
            editing_label = f" · {tr('category_editor.editing_label').replace('{name}', active_cats[self._editing_cat_idx].name)}"

        self._scroll_col = ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        tr("category_editor.drag_hint"),
                        size=scaled(FONT_BODY),
                        color=t.TEXT,
                        font_family="monospace",
                    ),
                    padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                                       bottom=scaled(CAT_HINT_PAD_BOTTOM)),
                ),
                self._list,
                ft.Container(
                    content=ft.Row(
                        [
                            self._new_cat_field,
                            ft.Container(
                                content=ft.Text(tr("category_editor.add"), color=t.WHITE,
                                                size=scaled(FONT_BODY), weight=ft.FontWeight.W_500),
                                bgcolor=t.ACCENT,
                                border_radius=scaled(8),
                                padding=t.pad_sym(horizontal=scaled(CAT_ADD_BTN_PAD_H),
                                                  vertical=scaled(CAT_ADD_BTN_PAD_V)),
                                on_click=self._add_category,
                                ink=True,
                            ),
                        ],
                        spacing=scaled(GAP_LG),
                    ),
                    padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                                       top=scaled(BTN_PAD_V)),
                ),
                ft.Container(
                    content=self._cat_error,
                    padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H), bottom=scaled(4)),
                ),
                ft.Container(
                    content=ft.Text(
                        tr("category_editor.categories_count").replace("{count}", str(len(active_cats))) + editing_label,
                        size=scaled(FONT_BODY),
                        color=t.TEXT,
                        font_family="monospace",
                    ),
                    padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                                       bottom=scaled(CAT_HINT_PAD_BOTTOM)),
                    alignment=ft.Alignment(0, 0),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0,
        )
        return self._scroll_col

    def _scroll_to(self, key: str):
        try:
            self._scroll_col.scroll_to(key=key, duration=300)
        except Exception:
            pass

    def reset_editing(self):
        self._editing_cat_idx = None

    # -------------------------
    # ReorderableListView
    # -------------------------

    def _refresh_list(self, settings: AppSettings):
        self._list.controls.clear()

        active = [c for c in settings.categories if not c.deleted]

        for idx, cat in enumerate(active):
            if idx == self._editing_cat_idx:
                item = self._row_editing(cat, idx, settings)
            else:
                item = self._row(cat, idx, settings)

            # Key is IMPORTANT for stable reorder animations
            item.key = cat.id
            self._list.controls.append(item)

        try:
            self._list.update()
        except Exception:
            pass

    def _handle_reorder(self, e: ft.OnReorderEvent, settings: AppSettings):
        """
        Called after the user drops item (the UI animation happens live while dragging).
        We update the underlying settings order here and persist it.
        """
        active = [c for c in settings.categories if not c.deleted]
        deleted = [c for c in settings.categories if c.deleted]

        old = int(e.old_index)
        new = int(e.new_index)

        # Flutter-style adjustment: when moving down, index shifts after pop
        cat = active.pop(old)
        if old < new:
            new -= 1
        new = max(0, min(new, len(active)))
        active.insert(new, cat)

        settings.categories = active + deleted
        self._editing_cat_idx = None

        backend.save_settings(settings)
        self._on_rebuild()

    # -------------------------
    # Rows (drag via ⠿ handle only)
    # -------------------------

    def _row(self, cat: Category, idx: int, settings: AppSettings) -> ft.Control:
        name_text = ft.Text(
            cat.name,
            size=scaled(FONT_LG),
            color=t.TEXT,
            weight=ft.FontWeight.W_500,
            expand=True,
        )

        edit_btn = ft.Container(
            content=ft.Text("✎", size=scaled(FONT_LG), color=t.ACCENT, font_family="monospace"),
            bgcolor=t.alpha(t.ACCENT, "18"),
            border_radius=scaled(CAT_EDIT_RADIUS),
            border=t.border_all(scaled(BORDER_WIDTH), t.alpha(t.ACCENT, "44")),
            padding=t.pad_sym(horizontal=scaled(CAT_EDIT_PAD_H), vertical=scaled(CAT_EDIT_PAD_V)),
            on_click=lambda e, i=idx: self._start_edit(i),
            ink=True,
        )

        delete_btn = ft.Container(
            content=ft.Text("×", size=scaled(FONT_LG), color=t.RED, font_family="monospace"),
            bgcolor=t.alpha(t.RED, "18"),
            border_radius=scaled(CAT_EDIT_RADIUS),
            border=t.border_all(scaled(BORDER_WIDTH), t.alpha(t.RED, "33")),
            padding=t.pad_sym(horizontal=scaled(CAT_EDIT_PAD_H), vertical=scaled(CAT_EDIT_PAD_V)),
            on_click=lambda e, c=cat: self._delete_category(c, settings),
            ink=True,
        )

        drag_handle = ft.ReorderableDragHandle(
            mouse_cursor=ft.MouseCursor.GRAB,
            content=ft.Container(
                content=ft.Text("⠿", size=scaled(CAT_DRAG_HANDLE), color=t.TEXT_DIMMER, font_family="monospace"),
                padding=t.pad_sym(horizontal=scaled(CAT_DRAG_PAD_H), vertical=scaled(CAT_ROW_PAD_V)),
            ),
        )

        inner = ft.Row(
            [
                drag_handle,
                name_text,
                edit_btn,
                delete_btn,
            ],
            spacing=scaled(GAP_LG),
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Container(
            padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H)),
            border=t.border_bottom(),
            bgcolor=None,
            content=inner,
        )

    def _row_editing(self, cat: Category, idx: int, settings: AppSettings) -> ft.Control:
        self._edit_cat_field = ft.TextField(
            value=cat.name,
            autofocus=True,
            expand=True,
            key="edit_cat_field",
            on_focus=lambda e: self._scroll_to("edit_cat_field"),
            bgcolor=t.SURFACE2,
            border_color=t.ACCENT,
            border_radius=scaled(CAT_EDIT_FIELD_RADIUS),
            text_style=ft.TextStyle(size=scaled(FONT_LG), color=t.TEXT),
            content_padding=t.pad_sym(horizontal=scaled(DD_PAD_H), vertical=scaled(CAT_EDIT_FIELD_PAD_V)),
        )

        drag_handle = ft.ReorderableDragHandle(
            mouse_cursor=ft.MouseCursor.GRAB,
            content=ft.Container(
                content=ft.Text("⠿", size=scaled(CAT_DRAG_HANDLE), color=t.TEXT_DIMMER, font_family="monospace"),
                padding=t.pad_sym(horizontal=scaled(CAT_DRAG_PAD_H), vertical=scaled(7)),
            ),
        )

        inner = ft.Row(
            [
                drag_handle,
                self._edit_cat_field,
                ft.ElevatedButton(
                    "OK",
                    bgcolor=t.ACCENT,
                    color=t.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=scaled(CAT_EDIT_FIELD_RADIUS)),
                        padding=t.pad_sym(horizontal=scaled(DD_PAD_H), vertical=scaled(CAT_EDIT_PAD_V)),
                    ),
                    on_click=lambda e, i=idx: self._confirm_edit(i, settings),
                ),
            ],
            spacing=scaled(GAP_LG),
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Container(
            padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H)),
            border=t.border_bottom(),
            bgcolor=t.alpha(t.ACCENT, "0a"),
            content=inner,
        )

    # -------------------------
    # CRUD
    # -------------------------

    def _start_edit(self, idx: int):
        self._editing_cat_idx = idx
        self._on_rebuild()

    def _confirm_edit(self, idx: int, settings: AppSettings):
        active = [c for c in settings.categories if not c.deleted]
        if not (0 <= idx < len(active)):
            self._editing_cat_idx = None
            self._on_rebuild()
            return

        cat = active[idx]
        new_name = (self._edit_cat_field.value or "").strip()

        if new_name and new_name != cat.name:
            for c in active:
                if c.id != cat.id and c.name == new_name:
                    self._cat_error.value = tr("category_editor.category_exists")
                    try:
                        self._cat_error.update()
                    except Exception:
                        pass
                    return

            cat.name = new_name
            backend.save_settings(settings)

        self._cat_error.value = ""
        self._editing_cat_idx = None
        self._on_rebuild()

    def _add_category(self, e):
        settings: AppSettings = self.app_state.settings
        name = (self._new_cat_field.value or "").strip()
        if not name:
            return

        for c in settings.categories:
            if not c.deleted and c.name == name:
                self._cat_error.value = tr("category_editor.category_exists")
                try:
                    self._cat_error.update()
                except Exception:
                    pass
                return

        settings.ensure_category(name)
        backend.save_settings(settings)

        self._new_cat_field.value = ""
        self._cat_error.value = ""
        self._refresh_list(settings)

        try:
            self._new_cat_field.update()
            self._cat_error.update()
        except Exception:
            pass

    def _delete_category(self, cat: Category, settings: AppSettings):
        if cat in settings.categories:
            cat.deleted = True
            cat.name = "..."
            backend.save_settings(settings)

            if self._editing_cat_idx is not None:
                self._editing_cat_idx = None

            self._refresh_list(settings)
