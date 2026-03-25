# Locales — Translation Files

## Structure

Each language has a JSON file named by its ISO 639-1 code: `en.json`, `uk.json`, etc.

Supported languages are defined in `config/languages.json`.

## Key Naming Convention

Keys use **dot-notation** organized by screen/component:

```
{section}.{element}
```

### Sections

| Section | Description | Used in |
|---------|-------------|---------|
| `shell` | Tab bar labels, app shell | `app/shell.py` |
| `update` | App update dialog | `app/shell.py` |
| `transactions` | Transaction list screen | `frontend/screens/transactions/` |
| `period_tabs` | Daily/Weekly/Total tabs | `frontend/screens/transactions/period_tabs.py` |
| `summary` | Income/Expenses/Balance bar | `frontend/screens/transactions/summary_row.py` |
| `dashboard` | Dashboard screen | `frontend/screens/dashboard/` |
| `add_receipt` | Add/edit receipt screen | `frontend/screens/add_receipt/screen.py` |
| `receipt_form` | Receipt form fields | `frontend/screens/add_receipt/receipt_form.py` |
| `item_editor` | Item add/edit bottom sheet | `frontend/screens/add_receipt/item_editor.py` |
| `items_table` | Items table headers | `frontend/screens/add_receipt/items_table.py` |
| `ai` | AI receipt scanning | `frontend/screens/add_receipt/ai_handler.py` |
| `settings` | Settings screen | `frontend/screens/settings/` |
| `category_editor` | Category management | `frontend/screens/settings/category_editor.py` |
| `api_key_editor` | API key editor | `frontend/screens/settings/api_key_editor.py` |
| `components` | Shared UI components | `frontend/components/` |
| `months_short` | Abbreviated month names (1-12) | `frontend/theme.py` |
| `days_short` | Abbreviated day names (0=Mon, 6=Sun) | `frontend/theme.py` |
| `months_chart` | Two-letter month labels for charts | `frontend/screens/dashboard/bar_chart.py` |
| `default_categories` | Default category names by ID (1-12) | `backend/models.py` |

## Template Variables

Some strings contain `{variable}` placeholders, replaced at runtime:

- `{count}` — item/category count
- `{new_version}` — app version string
- `{percent}` — progress percentage
- `{name}` — category name
- `{path}` — file path

## How to Add a New Language

1. Add the language to `config/languages.json`:
   ```json
   {"code": "pl", "name": "Polski"}
   ```

2. Create `locales/pl.json` with the same key structure as `en.json`.

3. Translate all values (keys must remain identical).

4. The language will automatically appear in Settings dropdown.

## Usage in Code

```python
from frontend.localisation import t

# Simple key
label = t("settings.title")  # → "Settings" or "Налаштування"

# With template variable
text = t("transactions.selected").replace("{count}", str(n))
```
