# THM Badge Generator Script
- Fetches TryHackMe user stats
- Generates a badge HTML
- Renders it as a 320x88 PNG image
- Saves to OUTPUT_PATH

## Dependencies:
  - pip install requests jinja2 playwright
  - playwright install chromium

## Usage

### As a Python Script

```bash
python3 thm_badge.py <USERNAME> <OUTPUT_PATH>
```

### As a GitHub Action

You can use this repository as a reusable GitHub Action in your workflows:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Generate badge
        uses: ./
        with:
          username: 'your-thm-username'
```

**Inputs:**
- `username` (required): The TryHackMe username to generate the badge for.

**Note:** Ensure your workflow installs dependencies and Playwright browsers as needed. See `.github/workflows/test.yml` for a working example.