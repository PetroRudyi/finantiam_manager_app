# Expense Tracker

A minimalist app for tracking expenses and income.
Built with [Flet](https://flet.dev/) >= 0.80.0 (Python).

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run
python main.py
```

---

## Project Structure

```
finance_manager/
├── main.py                        # Entry point
├── requirements.txt
├── app/
│   ├── state.py                   # Centralized app state
│   ├── shell.py                   # Tab bar, navigation, FAB
│   └── migration.py               # Background exchange rate migration
├── backend/
│   ├── models.py                  # Pydantic: Receipt, InvoiceItem, AppSettings
│   ├── config.py                  # Currency/category/language configuration
│   ├── analytics.py               # Receipt analytics
│   ├── exchange_service.py        # Currency exchange rates (with caching)
│   ├── update_service.py          # App version checking
│   ├── ai_service.py              # Gemini AI receipt recognition
│   └── storage/
│       ├── _paths.py              # File path definitions
│       ├── settings.py            # Settings persistence (JSON)
│       ├── receipts.py            # Receipt persistence (JSON)
│       ├── export.py              # CSV export
│       └── recalculation.py       # Batch exchange rate recalculation
├── frontend/
│   ├── localisation.py            # Translation module
│   ├── theme.py                   # Colors, typography helpers (Flet 0.80+)
│   ├── helpers.py                 # Utility functions
│   └── screens/
│       ├── transactions/          # Transactions list screen
│       ├── dashboard/             # Analytics dashboard
│       ├── add_receipt/           # Receipt entry & editing
│       └── settings/              # Settings screen
├── config/                        # Static configuration files
│   ├── currencies.json
│   ├── categories.json
│   ├── app.json
│   └── languages.json
└── locales/                       # Translation files
    ├── en.json
    └── uk.json
```

---

## Data Storage

App data is stored **outside the project directory** to prevent test data from leaking into APK builds.

| Platform | Path                                                                                           |
|---|------------------------------------------------------------------------------------------------|
| **Android / iOS** | `FLET_APP_STORAGE_DATA` (set by Flet runtime)                                                  |
| **Windows** | `%APPDATA%\finance_manager\`                                                                   |
| **Windows (MS Store Python)** | `%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.*\LocalCache\Roaming\finance_manager\` |
| **macOS** | `~/Library/Application Support/finance_manager/`                                               |
| **Linux** | `$XDG_DATA_HOME/finance_manager/` (`~/.local/share/finance_manager/`)                          |

Important: can be in python local AppData. Not Windows`s one.

Stored files:

| File | Contents |
|---|---|
| `receipts.json` | All receipts |
| `settings.json` | User settings (currency, language, theme, categories) |
| `gemini_api_key.json` | Gemini API key (separate for security) |
| `exchange_rates.json` | Cached exchange rates |
| `export.csv` | Generated on export |

The directory is created automatically on first launch.

---

## AI Receipt Recognition

1. Get an API key: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Paste it in **Settings → Gemini API Key**
3. In the receipt form, click **Upload Receipt Photo (AI)**
4. All fields will be filled in automatically

---

## Requirements

- Python 3.10+
- Flet 0.80+
