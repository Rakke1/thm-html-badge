# THM Badge Generator Script
- Fetches TryHackMe user stats
- Generates a badge HTML
- Renders it as a 320x88 PNG image
- Saves to OUTPUT_PATH

## Dependencies:
  - pip install requests jinja2 playwright
  - playwright install chromium

## Usage:

```bash
python3 thm_badge.py <USERNAME> <OUTPUT_PATH>
```