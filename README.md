# python-roadmap

Small Python project for scraping quotes from [quotes.toscrape.com](https://quotes.toscrape.com), cleaning the results, and generating simple analytics.

## What it does
- `main.py` exposes a FastAPI app with quote-scraping endpoints.
- `analyze.py` reads the cleaned CSV and generates `top_authors.png` and `tag_wordcloud.png`.
- `ai_analysis.py` adds Hugging Face sentiment labels and writes `quotes_with_ai.csv`.

## Requirements
- Python 3.13
- A virtual environment in `.venv`

## Setup
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run
Start the API:
```powershell
.\.venv\Scripts\python.exe main.py
```

Generate charts from the cleaned CSV:
```powershell
.\.venv\Scripts\python.exe analyze.py
```

Run sentiment analysis:
```powershell
.\.venv\Scripts\python.exe ai_analysis.py
```

## Outputs
- `quotes.json_cleaned.csv`
- `quotes_with_ai.csv`
- `top_authors.png`
- `tag_wordcloud.png`

## Notes
- Generated files are written to the repository root.
- On Windows, `analyze.py` uses `matplotlib` in headless mode so charts can render without a GUI.
