import snowflake.connector
import pandas as pd
import os
from datetime import datetime

def download_daily_data():
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        warehouse=os.environ['SNOWFLAKE_WAREHOUSE']
    )
    
    try:
        cursor = conn.cursor()
        
        # Ensure data directory exists
        os.makedirs('datasets', exist_ok=True)
        
        # Download NEWS table
        print("Downloading BTC_DATA.RAW.BITCOIN_NEWS...")
        cursor.execute("SELECT DATETIME,HEADLINE,SUMMARY,SOURCE,URL,CATEGORIES,TAGS FROM BTC_DATA.RAW.BITCOIN_NEWS ORDER BY DATETIME ASC")
        df_news = cursor.fetch_pandas_all()
        df_news.to_csv('datasets/news.csv', index=False)
        print(f"Saved news data: {len(df_news)} rows")
        
        # Download DAILY_FNG table
        print("Downloading BTC_DATA.ANALYTICS.DAILY_FNG...")
        cursor.execute("SELECT ANALYSIS_DATE,DAILY_FEAR_GREED_SCORE,FEAR_GREED_CATEGORY,TOTAL_ARTICLES,HOURLY_SCORES,PROCESSING_TIMESTAMP FROM BTC_DATA.ANALYTICS.DAILY_FNG ORDER BY ANALYSIS_DATE ASC")
        df_daily_fng = cursor.fetch_pandas_all()
        df_daily_fng.to_csv('datasets/daily_fng.csv', index=False)
        print(f"Saved daily FNG data: {len(df_daily_fng)} rows")
        
    except Exception as e:
        print(f"Error downloading daily data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    download_daily_data()
