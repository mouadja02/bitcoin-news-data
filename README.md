# Bitcoin News Data Collection

A comprehensive dataset of Bitcoin-related news articles and market sentiment indicators collected hourly from multiple cryptocurrency news sources.

## Dataset Overview

This repository contains:
- **Hourly Bitcoin news articles** from May-June 2025
- **Bitcoin Fear & Greed Index** historical data
- News data sourced from major Bitcoin publications via CoinDesk and Finnhub APIs
- Structured CSV format for easy analysis and research

## Data Structure

### News Data Files
```
DDMMYYYY/
├── bitcoin_news_YYYY-MM-DD_HH-00.csv
XX052025.zip (May 2025 complete dataset - compressed)
XX062025.zip (June 2025 complete dataset - compressed)
```

Each hourly news file contains:
- `datetime`: Publication timestamp (ISO 8601 format)
- `headline`: Article title
- `summary`: Article summary/excerpt
- `source`: Publication source (e.g., Forbes, Bitcoin.com, CoinTelegraph)
- `url`: Direct link to the article
- `categories`: Topic categories (BTC, BUSINESS, MARKET, etc.)
- `tags`: Relevant tags and metadata
- `api_source`: Data collection source (CoinDesk API, Finnhub API)

### Fear & Greed Index
`bitcoin_fng_index.csv` contains:
- `date`: Date (YYYY-MM-DD format)
- `time`: Hour (HH:MM format)
- `score`: Numerical score (0-100)
- `fng_class`: Classification (Fear, Neutral, Greed, Extreme Greed)

## Use Cases

- **Sentiment Analysis**: Correlate news sentiment with price movements
- **Market Research**: Analyze Bitcoin news coverage patterns
- **Academic Research**: Study cryptocurrency media influence
- **Trading Strategy Development**: Incorporate news sentiment into models
- **Data Science Projects**: Practice NLP and time series analysis

## Data Coverage

- **Time Period**: May 5 - June 26, 2025
- **Update Frequency**: Hourly
- **Languages**: English
- **API Sources**: CoinDesk API, Finnhub API

### Archive Structure
- `XX052025.zip`: Complete May 2025 dataset (compressed for storage efficiency)
- `XX062025.zip`: Complete June 2025 dataset (compressed for storage efficiency)
- Individual daily folders for July 2025 (uncompressed for easy access)

## Getting Started

### Prerequisites
- Python 3.7+
- pandas
- matplotlib (for visualizations)
- jupyter notebook (optional)

### Quick Start
```python
import pandas as pd
import glob
import zipfile

# Extract a compressed data if needed
with zipfile.ZipFile('XX052025.zip', 'r') as zip_ref: 
    zip_ref.extractall('may_2025_data/')

# Load all news data (June)
news_files = glob.glob("*/bitcoin_news_*.csv")
all_news = pd.concat([pd.read_csv(f) for f in news_files], ignore_index=True)

# Load May data (if extracted)
may_files = glob.glob("may_2025_data/*/bitcoin_news_*.csv")
if may_files:
    may_news = pd.concat([pd.read_csv(f) for f in may_files], ignore_index=True)
    all_news = pd.concat([may_news, all_news], ignore_index=True)

# Load Fear & Greed Index
fng_data = pd.read_csv("bitcoin_fng_index.csv")

# Basic analysis
print(f"Total articles: {len(all_news)}")
print(f"Date range: {all_news['datetime'].min()} to {all_news['datetime'].max()}")
print(f"Top sources: {all_news['source'].value_counts().head()}")
print(f"API sources: {all_news['api_source'].value_counts()}")

# Run your pretrained sentiment analyzer model to get the hourly fear and greed index
```


## Data Quality

- All timestamps are in UTC
- Duplicate articles have been filtered
- URLs are validated and accessible
- Missing data is clearly marked

## Limitations
- Data collection limited to English-language sources
- Some sources may have rate limiting affecting completeness
- Sentiment analysis included, but updated once every two weeks
- No price data included (this repo focuses on news and sentiment only), if you need price dataset, check this repo: https://github.com/mouadja02/bitcoin-hourly-ohclv-dataset.git

## License

This dataset is provided for research and educational purposes. Please respect the original publishers' terms of service when using the news content.

**Disclaimer**: This data is for research purposes only. Always verify information from original sources before making financial decisions.
