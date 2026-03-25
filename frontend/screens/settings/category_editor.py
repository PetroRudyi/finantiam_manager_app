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
from frontend.localisation import t as tr


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

    def build(self) -> ft.Column:
        settings: AppSettings = self.app_state.settings

        self._new_cat_field = ft.TextField(
            hint_text=tr("category_editor.new_category_hint"),
            bgcolor=t.SURFACE2,
            border_color=t.BORDER,
            focused_border_color=t.ACCENT,
            border_radius=8,
            expand=True,
            text_style=ft.TextStyle(size=12, color=t.TEXT),
            hint_style=ft.TextStyle(size=12, color=t.TEXT_DIMMER),
            content_padding=t.pad_sym(horizontal=10, vertical=7),
        )

        self._cat_error = ft.Text("", size=10, color=t.RED)

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

        return ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        tr("category_editor.drag_hint"),
                        size=9,
                        color=t.TEXT_DIMMER,
                        font_family="monospace",
                    ),
                    padding=t.pad_only(left=18, right=18, bottom=8),
                ),
                self._list,
                ft.Container(
                    content=ft.Row(
                        [
                            self._new_cat_field,
                            ft.ElevatedButton(
                                tr("category_editor.add"),
                                bgcolor=t.ACCENT,
                                color=t.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=t.pad_sym(horizontal=14, vertical=7),
                                ),
                                on_click=self._add_category,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=t.pad_sym(horizontal=18, vertical=10),
                ),
                ft.Container(
                    content=self._cat_error,
                    padding=t.pad_only(left=18, right=18, bottom=4),
                ),
                ft.Container(
                    content=ft.Text(
                        tr("category_editor.categories_count").replace("{count}", str(len(active_cats))) + editing_label,
                        size=9,
                        color=t.TEXT_DIMMER,
                        font_family="monospace",
                    ),
                    padding=t.pad_only(left=18, right=18, bottom=8),
                    alignment=ft.Alignment(0, 0),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0,
        )

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
    # Rows (drag whole row)
    # -------------------------

    def _row_shell(self, content: ft.Control) -> ft.Container:
        return ft.Container(
            padding=t.pad_only(left=18, right=18, top=9, bottom=9),
            border=t.border_bottom(),
            bgcolor=None,
            content=content,
        )

    def _row(self, cat: Category, idx: int, settings: AppSettings) -> ft.Control:
        name_text = ft.Text(
            cat.name,
            size=13,
            color=t.TEXT,
            weight=ft.FontWeight.W_500,
            expand=True,
        )

        edit_btn = ft.Container(
            content=ft.Text("✎", size=10, color=t.ACCENT, font_family="monospace"),
            bgcolor=t.alpha(t.ACCENT, "18"),
            border_radius=5,
            border=t.border_all(1, t.alpha(t.ACCENT, "44")),
            padding=t.pad_sym(horizontal=8, vertical=3),
            on_click=lambda e, i=idx: self._start_edit(i),
            ink=True,
        )

        delete_btn = ft.Container(
            content=ft.Text("×", size=10, color=t.RED, font_family="monospace"),
            bgcolor=t.alpha(t.RED, "18"),
            border_radius=5,
            border=t.border_all(1, t.alpha(t.RED, "33")),
            padding=t.pad_sym(horizontal=8, vertical=3),
            on_click=lambda e, c=cat: self._delete_category(c, settings),
            ink=True,
        )

        inner = ft.Row(
            [
                ft.Text("⠿", size=14, color=t.TEXT_DIMMER, font_family="monospace"),
                name_text,
                edit_btn,
                delete_btn,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Make the WHOLE row the drag start area:
        return ft.ReorderableDragHandle(
            mouse_cursor=ft.MouseCursor.GRAB,
            content=self._row_shell(inner),
        )

    def _row_editing(self, cat: Category, idx: int, settings: AppSettings) -> ft.Control:
        self._edit_cat_field = ft.TextField(
            value=cat.name,
            autofocus=True,
            expand=True,
            bgcolor=t.SURFACE2,
            border_color=t.ACCENT,
            border_radius=7,
            text_style=ft.TextStyle(size=13, color=t.TEXT),
            content_padding=t.pad_sym(horizontal=10, vertical=5),
        )

        inner = ft.Row(
            [
                ft.Text("⠿", size=14, color=t.TEXT_DIMMER, font_family="monospace"),
                self._edit_cat_field,
                ft.ElevatedButton(
                    "OK",
                    bgcolor=t.ACCENT,
                    color=t.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=7),
                        padding=t.pad_sym(horizontal=10, vertical=3),
                    ),
                    on_click=lambda e, i=idx: self._confirm_edit(i, settings),
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.ReorderableDragHandle(
            mouse_cursor=ft.MouseCursor.GRAB,
            content=ft.Container(
                padding=t.pad_only(left=18, right=18, top=7, bottom=7),
                border=t.border_bottom(),
                bgcolor=t.alpha(t.ACCENT, "0a"),
                content=inner,
            ),
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