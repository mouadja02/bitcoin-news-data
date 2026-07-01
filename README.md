# Bitcoin News Dataset

A comprehensive dataset of Bitcoin-related news articles collected from multiple sources, stored in Apache Parquet format for efficient analysis.

## Dataset Overview

This repository contains a continuously-updated dataset of Bitcoin news articles with metadata including publication timestamps, headlines, summaries, source information, and categorization. Data is sourced from The Guardian, Finnhub, and AlphaVantage APIs.

## How the Dataset is Built

This dataset is automatically generated and published by an [Airflow DAG](https://github.com/mouadja02/airflow-self-hosted) running on a self-hosted Raspberry Pi. The pipeline:

1. **Collects news** from three sources daily:
   - **The Guardian API** — Historical backfill (from 2014) + daily delta
   - **Finnhub API** — Daily crypto news
   - **AlphaVantage NEWS_SENTIMENT** — Daily sentiment-tagged news
2. **Deduplicates** articles by URL and merges into a Snowflake data warehouse
3. **Exports** the full table as a Parquet file and pushes to this repo via Git LFS

The DAG runs daily at 01:00 UTC. Each run fetches new articles from all three sources and re-exports the complete dataset.

## Repository Structure

```
bitcoin-news-data/
├── bitcoin-news.parquet      # Complete dataset — Parquet format (Git LFS)
├── bitcoin-news.tsv          # Complete dataset — TSV format (Git LFS)
├── scripts/
│   ├── bitcoin_news_dag.py       # Reference copy of the Airflow DAG
│   ├── download_daily_data.py    # Utility to download from Snowflake
│   └── download_hourly_data.py   # Utility to download hourly FNG data
├── LICENSE
└── README.md
```

## Data Schema

The `bitcoin-news.parquet` file contains the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `DATETIME` | timestamp | Publication timestamp |
| `HEADLINE` | string | Article title |
| `SUMMARY` | string | Article summary/excerpt |
| `SOURCE` | string | Publication source (The Guardian, Finnhub, etc.) |
| `URL` | string | Direct link to the article |
| `CATEGORIES` | string | Topic categories |
| `TAGS` | string | Relevant tags and metadata |
| `API_SOURCE` | string | Which API provided the article (`guardian`, `finnhub`, `alphavantage`) |
| `FILE_NAME` | string | Internal batch identifier |
| `CREATED_AT` | timestamp | When the record was ingested |

## Why Parquet + TSV?

The dataset is published in two formats:

| Format | File | Best for |
|--------|------|----------|
| **Parquet** | `bitcoin-news.parquet` | Python/R analysis, fast columnar reads, type-safe timestamps |
| **TSV** | `bitcoin-news.tsv` | Universal compatibility, human-readable, shell tools (`cut`, `awk`) |

Why not CSV? Headlines and summaries contain commas, quotes, and HTML fragments that break comma-delimited parsing. TSV (tab-separated) avoids this since tabs almost never appear in news text.

Parquet additionally provides:
- **50-70% smaller** file size via Snappy compression
- **Native types** — timestamps stay as timestamps, not strings
- **Column pruning** — read only the columns you need

## Quick Start

```python
import pandas as pd

# Load from Parquet (recommended for Python)
df = pd.read_parquet("bitcoin-news.parquet")

# Or load from TSV
df = pd.read_csv("bitcoin-news.tsv", sep="\t")

# Filter by source
guardian = df[df["API_SOURCE"] == "guardian"]

# Get articles from last 30 days
from datetime import datetime, timedelta
recent = df[df["DATETIME"] >= datetime.now() - timedelta(days=30)]
```

```python
# Using polars (faster for large datasets)
import polars as pl

df = pl.read_parquet("bitcoin-news.parquet")
df.filter(pl.col("SOURCE") == "The Guardian").select(["DATETIME", "HEADLINE"])
```

```bash
# Shell — quick look at TSV without any code
head -5 bitcoin-news.tsv | column -t -s $'\t'
```

## Data Coverage

- **Time Period**: 2014 – Present (continuously updated)
- **Update Frequency**: Daily (01:00 UTC)
- **Languages**: English
- **Sources**: The Guardian, Finnhub, AlphaVantage

## Use Cases

- Sentiment analysis — correlate news tone with Bitcoin price movements
- Market research — analyze Bitcoin coverage patterns over time
- NLP projects — named entity recognition, topic modeling, summarization
- Trading signals — incorporate news sentiment into algorithmic strategies
- Academic research — study cryptocurrency media influence on market behavior

## Limitations

- English-language sources only
- Some API rate limiting may affect completeness on individual days
- No price data included (news and metadata only) — for price data see [bitcoin-hourly-ohlcv-dataset](https://github.com/mouadja02/bitcoin-hourly-ohclv-dataset)

## License

MIT License. See [LICENSE](LICENSE) for details.

This data is for research and educational purposes. Please respect the original publishers' terms of service when using the news content.

**Disclaimer**: This data is for research purposes only. Always verify information from original sources before making financial decisions.
