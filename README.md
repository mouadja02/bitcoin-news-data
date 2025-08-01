# Bitcoin News Data Collection

A comprehensive dataset of Bitcoin-related news articles and market sentiment indicators, featuring Fear & Greed Index calculations based on sentiment analysis of Bitcoin news coverage.

## Dataset Overview

This repository contains:
- **Bitcoin news articles** with comprehensive metadata
- **Daily Fear & Greed Index** with aggregated sentiment scores
- **Hourly Fear & Greed Index** with detailed temporal analysis
- Data sourced from major Bitcoin publications and processed through advanced sentiment analysis
- Structured CSV format optimized for analysis and research

## Repository Structure

```
bitcoin-news-data/
├── datasets/
│   ├── news.csv              # Complete Bitcoin news dataset
│   ├── daily_fng.csv         # Daily Fear & Greed Index aggregations
│   └── hourly_fng.csv        # Hourly Fear & Greed Index calculations
├── scripts/
│   ├── download_daily_data.py    # Script to download news and daily FNG data
│   └── download_hourly_data.py   # Script to download hourly FNG data
└── README.md
```

## Data Structure

### News Data (`news.csv`)
Contains comprehensive Bitcoin news articles with the following fields:
- `DATETIME`: Publication timestamp (ISO format)
- `HEADLINE`: Article title
- `SUMMARY`: Article summary/excerpt  
- `SOURCE`: Publication source
- `URL`: Direct link to the article
- `CATEGORIES`: Topic categories (comma-separated)
- `TAGS`: Relevant tags and metadata

### Daily Fear & Greed Index (`daily_fng.csv`)
Daily aggregated sentiment analysis with:
- `ANALYSIS_DATE`: Date of analysis (YYYY-MM-DD)
- `DAILY_FEAR_GREED_SCORE`: Aggregated daily score (0-100)
- `FEAR_GREED_CATEGORY`: Classification (Fear, Neutral, Greed, Extreme Greed)
- `TOTAL_ARTICLES`: Number of articles analyzed for that day
- `HOURLY_SCORES`: JSON array of hourly scores throughout the day
- `PROCESSING_TIMESTAMP`: Data processing timestamp

### Hourly Fear & Greed Index (`hourly_fng.csv`)
Detailed hourly sentiment analysis with:
- `DATETIME_HOUR`: Hour timestamp (YYYY-MM-DD HH:00:00)
- `AVG_SENTIMENT_SCORE`: Average sentiment score for the hour
- `FEAR_GREED_SCORE`: Normalized Fear & Greed score (0-100)
- `FEAR_GREED_CATEGORY`: Hourly classification
- `TOTAL_ARTICLES`: Number of articles analyzed for that hour
- `PROCESSING_TIMESTAMP`: Data processing timestamp

## Use Cases

- **Sentiment Analysis**: Correlate news sentiment with Bitcoin price movements
- **Market Research**: Analyze Bitcoin news coverage patterns and trends
- **Academic Research**: Study cryptocurrency media influence on market behavior
- **Trading Strategy Development**: Incorporate news sentiment into algorithmic trading models
- **Data Science Projects**: Practice NLP, time series analysis, and sentiment modeling
- **Financial Analysis**: Research Fear & Greed cycles in cryptocurrency markets

## Data Coverage & Statistics

- **Time Period**: May 2025 - Present (continuously updated)
- **Total Articles**: 50MB+ of comprehensive Bitcoin news coverage
- **Update Frequency**: Real-time collection with hourly aggregations
- **Languages**: English
- **API Sources**: CoinDesk API, Finnhub API


## Limitations
- Data collection limited to English-language sources
- Some sources may have rate limiting affecting completeness
- Sentiment analysis included, but updated once every two weeks
- No price data included (this repo focuses on news and sentiment only), if you need price dataset, check this repo: https://github.com/mouadja02/bitcoin-hourly-ohclv-dataset.git

## License

This dataset is provided under the MIT License. See LICENSE file for details.

It is provided for research and educational purposes. Please respect the original publishers' terms of service when using the news content.

**Disclaimer**: This data is for research purposes only. Always verify information from original sources before making financial decisions.
