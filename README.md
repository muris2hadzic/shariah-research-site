# Site skeleton

A Quarto website for Shariah-compliant investment research. Search the project for `TODO` to find everything that needs your input.

## Preview on your computer

1. Install Quarto: https://quarto.org/docs/get-started/
2. In this folder, run `quarto preview`. A browser tab opens and refreshes as you edit.

## Layout

| Path | What it is |
|---|---|
| `_quarto.yml` | Site title, navigation, footer, theme |
| `index.qmd`, `about.qmd`, `methodology.qmd`, `glossary.qmd`, `disclosures.qmd` | Foundation pages |
| `research/` | One `.qmd` file per article; the listing page updates itself |
| `strategies/` | One `.qmd` file per strategy; each reads a data file |
| `data/strategies/` | Frozen backtest results, one JSON file per strategy |
| `data/signals/` | Reserved for live signals (later) |
| `scripts/fetch_backtest.py` | Pulls a backtest from QuantConnect into `data/strategies/` |
| `.github/workflows/publish.yml` | Publishes to GitHub Pages on push |

## Add a research article

Copy `research/2026-10-07-example-article.qmd`, rename it, edit. Put images in `research/images/`.

## Add a strategy

1. Set credentials (never commit them):
   `export QC_USER_ID=...` and `export QC_API_TOKEN=...`
2. `pip install requests`
3. `python scripts/fetch_backtest.py --project <id> --backtest <id> --slug my-strategy`
4. Copy `strategies/example-strategy.qmd` to `strategies/my-strategy.qmd` and change the file name inside it to `my-strategy.json`.

## Put it on a staging address (GitHub Pages)

```
git init -b main
git add .
git commit -m "Site skeleton"
```

Create an empty repository on GitHub, then:

```
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

In the repository: Settings -> Pages -> Source -> "GitHub Actions". The site appears at `https://<you>.github.io/<repo>/` after the first build. Connect your own domain later from the same settings page.

Note: on the free GitHub plan, Pages requires a public repository. Keep strategy code in QuantConnect, not here.

## Before launch

- Replace every `TODO`
- Delete the example article and example strategy (and its sample data file)
- Have counsel review `disclosures.qmd`
