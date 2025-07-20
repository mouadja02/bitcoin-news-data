import snowflake.connector
import pandas as pd
import os
from datetime import datetime

def download_hourly_fng():
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        warehouse=os.environ['SNOWFLAKE_WAREHOUSE']
    )
    
    try:
        cursor = conn.cursor()
        
        # Download HOURLY_FNG table
        print("Downloading BTC_DATA.ANALYTICS.HOURLY_FNG...")
        cursor.execute("SELECT DATETIME_HOUR,AVG_SENTIMENT_SCORE,FEAR_GREED_SCORE,FEAR_GREED_CATEGORY,TOTAL_ARTICLES,PROCESSING_TIMESTAMP FROM BTC_DATA.ANALYTICS.HOURLY_FNG ORDER BY DATETIME_HOUR ASC")
        df_hourly = cursor.fetch_pandas_all()
        
        # Ensure data directory exists
        os.makedirs('datasets', exist_ok=True)
        
        # Save to CSV
        df_hourly.to_csv('datasets/hourly_fng.csv', index=False)
        print(f"Saved hourly FNG data: {len(df_hourly)} rows")
        
    except Exception as e:
        print(f"Error downloading hourly data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    download_hourly_fng()
