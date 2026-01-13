# Windows Playwright Installation Fix

## The Problem

On Windows, running `playwright install chromium` directly gives:
```
playwright : The term 'playwright' is not recognized...
```

## The Solution

Use Python's module syntax instead:

```bash
python -m playwright install chromium
```

## Why This Happens

- `playwright` is a Python package, not a system command
- On Windows, Python scripts aren't always in PATH
- Using `python -m` ensures Python finds the module correctly

## Complete Installation Steps (Windows)

1. **Install packages:**
   ```bash
   pip install TikTokApi playwright
   ```

2. **Install Chromium browser:**
   ```bash
   python -m playwright install chromium
   ```

3. **Verify installation:**
   ```bash
   python -m playwright --version
   ```

## Alternative: Use Full Python Path

If `python` doesn't work, use the full path:

```bash
C:\Python311\python.exe -m playwright install chromium
```

Or if using Python from Microsoft Store:

```bash
python3 -m playwright install chromium
```

## Verify It Worked

After installation, you should see:
- Chromium downloaded (~122 MB)
- FFMPEG downloaded (~1.4 MB)
- Files in: `C:\Users\<YourUser>\AppData\Local\ms-playwright\`

## Test TikTok Scraper

```bash
python test_tiktok_scraper.py
```

If Chromium is installed correctly, the scraper will work!
