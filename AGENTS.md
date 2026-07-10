# Repository Guidelines

## Project Structure & Module Organization
- `main.py` exposes the FastAPI scraper and CSV export endpoints.
- `analyze.py` reads `quotes.json_cleaned.csv` and generates `top_authors.png` and `tag_wordcloud.png`.
- `ai_analysis.py` adds Hugging Face sentiment analysis and writes `quotes_with_ai.csv`.
- Generated artifacts live in the repo root. Keep reusable code in functions so scripts stay easy to run and inspect.

## Build, Test, and Development Commands
- `.\.venv\Scripts\python.exe main.py` starts the API on `127.0.0.1:8000`.
- `.\.venv\Scripts\python.exe analyze.py` regenerates the chart outputs from the cleaned CSV.
- `.\.venv\Scripts\python.exe ai_analysis.py` runs sentiment analysis and writes `quotes_with_ai.csv`.
- There is no separate build step. If you need a quick smoke check, run the relevant script and confirm the output files were updated.

## Coding Style & Naming Conventions
- Use 4-space indentation, `snake_case` for functions and variables, and `PascalCase` only for classes.
- Keep functions small and explicit; prefer pure helpers such as `parse_quotes()` and `load_data()`.
- Save files with UTF-8 encoding. For plotting on Windows, keep `matplotlib.use("Agg")` for headless runs.
- Use descriptive output names such as `quotes_with_ai.csv` and `top_authors.png`.

## Testing Guidelines
- No automated test suite is currently checked in.
- When adding tests, place them under `tests/` and name them `test_*.py`.
- Focus tests on deterministic helpers: parsing HTML, loading CSVs, and transforming DataFrames.

## Commit & Pull Request Guidelines
- No Git history is available in this workspace, so no repository-specific commit convention can be verified.
- Use short, imperative commits such as `feat: add sentiment export` or `fix: handle missing csv`.
- PRs should include a summary, the commands you ran, and screenshots or sample output when charts or CSVs change.

## Data & Dependency Notes
- Do not commit large regenerated outputs unless they are intentionally part of the repo.
- If you add dependencies, document the install command in the README or a requirements file.
