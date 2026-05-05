"""
Bitcoin News DAG - Production Version
Fetches Bitcoin news from multiple APIs and stores in Snowflake with duplicate prevention
"""

from datetime import datetime, timedelta
import os
import json
import requests
import csv
import base64
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SQLExecuteQueryOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

# Default arguments
default_args = {
    'owner': 'mouad-jaouhari',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'bitcoin_news',
    default_args=default_args,
    description='Fetch Bitcoin news and store in Snowflake with duplicate prevention',
    schedule='0 * * * *',  # Every hour
    catchup=False,
    tags=['bitcoin', 'news', 'snowflake', 'production'],
)

def get_last_datetime_from_snowflake():
    """Get the latest datetime from Snowflake to avoid duplicates"""
    
    hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    
    try:
        result = hook.get_first("""
            SELECT COALESCE(MAX(datetime), '1970-01-01 00:00:00'::TIMESTAMP) as max_datetime
            FROM BTC_DATA.RAW.BITCOIN_NEWS
        """)
        
        if result and result[0]:
            return result[0]
        else:
            # If no records exist, return epoch time
            return datetime(1970, 1, 1)
            
    except Exception as e:
        print(f"Error getting last datetime from Snowflake: {str(e)}")
        # Return epoch time as fallback
        return datetime(1970, 1, 1)

def fetch_cryptocompare_news(**context):
    """Fetch Bitcoin news from CryptoCompare API"""
    
    # Get the last datetime to avoid duplicates
    last_datetime = get_last_datetime_from_snowflake()
    print(f"Last datetime in Snowflake: {last_datetime}")
    
    url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN&categories=BTC"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        processed_data = []
        if data.get('Data') and isinstance(data['Data'], list):
            for news in data['Data']:
                # Convert timestamp to datetime for comparison
                news_datetime = datetime.fromtimestamp(news.get('published_on', 0))
                
                # Only process articles newer than the last one in Snowflake
                if news_datetime > last_datetime:
                    processed_news = {
                        'datetime': news_datetime.isoformat(),
                        'headline': news.get('title', ''),
                        'summary': news.get('body', ''),
                        'source': news.get('source', ''),
                        'url': news.get('url', ''),
                        'categories': str(news.get('categories', '')),
                        'tags': str(news.get('tags', '')),
                        'api_source': 'cryptocompare'
                    }
                    processed_data.append(processed_news)
        
        print(f"CryptoCompare: Found {len(processed_data)} new articles")
        context['task_instance'].xcom_push(key='cryptocompare_news', value=processed_data)
        return len(processed_data)
        
    except Exception as e:
        print(f"Failed to fetch CryptoCompare news: {str(e)}")
        context['task_instance'].xcom_push(key='cryptocompare_news', value=[])
        return 0

def fetch_finnhub_news(**context):
    """Fetch Bitcoin news from Finnhub API"""
    
    # Get the last datetime to avoid duplicates
    last_datetime = get_last_datetime_from_snowflake()
    
    api_key = os.getenv('FINNHUB_API_KEY')
    if not api_key:
        print("Finnhub API key not found")
        context['task_instance'].xcom_push(key='finnhub_news', value=[])
        return 0
    
    url = f"https://finnhub.io/api/v1/news?category=crypto&token={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        processed_data = []
        if isinstance(data, list):
            for news in data:
                # Convert timestamp to datetime for comparison
                news_datetime = datetime.fromtimestamp(news.get('datetime', 0))
                
                # Only process articles newer than the last one in Snowflake
                if (news_datetime > last_datetime and 
                    news.get('summary') and news.get('summary').strip()):
                    
                    processed_news = {
                        'datetime': news_datetime.isoformat(),
                        'headline': news.get('headline', ''),
                        'summary': news.get('summary', ''),
                        'source': news.get('source', ''),
                        'url': news.get('url', ''),
                        'categories': '',  # Finnhub doesn't provide categories
                        'tags': '',        # Finnhub doesn't provide tags
                        'api_source': 'finnhub'
                    }
                    processed_data.append(processed_news)
        
        print(f"Finnhub: Found {len(processed_data)} new articles")
        context['task_instance'].xcom_push(key='finnhub_news', value=processed_data)
        return len(processed_data)
        
    except Exception as e:
        print(f"Failed to fetch Finnhub news: {str(e)}")
        context['task_instance'].xcom_push(key='finnhub_news', value=[])
        return 0

def merge_and_deduplicate_news(**context):
    """Merge news from different sources and remove duplicates"""
    
    cryptocompare_news = context['task_instance'].xcom_pull(task_ids='fetch_cryptocompare_news', key='cryptocompare_news') or []
    finnhub_news = context['task_instance'].xcom_pull(task_ids='fetch_finnhub_news', key='finnhub_news') or []
    
    # Merge all news
    all_news = cryptocompare_news + finnhub_news
    
    # Remove duplicates based on summary and URL
    seen_items = set()
    unique_news = []
    
    for news in all_news:
        # Create a unique key based on summary and URL
        summary_key = news.get('summary', '').strip().lower()
        url_key = news.get('url', '').strip().lower()
        unique_key = f"{summary_key}|{url_key}"
        
        if unique_key not in seen_items and summary_key:
            seen_items.add(unique_key)
            unique_news.append(news)
    
    print(f"CryptoCompare items: {len(cryptocompare_news)}")
    print(f"Finnhub items: {len(finnhub_news)}")
    print(f"Original items: {len(all_news)}, Unique items: {len(unique_news)}, Duplicates removed: {len(all_news) - len(unique_news)}")
    
    context['task_instance'].xcom_push(key='unique_news', value=unique_news)
    context['task_instance'].xcom_push(key='cryptocompare_count', value=len(cryptocompare_news))
    context['task_instance'].xcom_push(key='finnhub_count', value=len(finnhub_news))
    context['task_instance'].xcom_push(key='total_count', value=len(unique_news))
    
    return len(unique_news)

def insert_news_to_snowflake(**context):
    """Insert unique news articles into Snowflake"""
    
    unique_news = context['task_instance'].xcom_pull(task_ids='merge_and_deduplicate_news', key='unique_news') or []
    
    if not unique_news:
        print("No new articles to insert")
        return "No new articles to insert"
    
    hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    
    # Prepare insert statement
    insert_sql = """
    INSERT INTO BTC_DATA.RAW.BITCOIN_NEWS 
    (datetime, headline, summary, source, url, categories, tags, api_source, file_name)
    VALUES (
        TRY_TO_TIMESTAMP(%s),
        %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    try:
        # Generate file name for tracking
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M')
        file_name = f"airflow_hourly_{current_time}.csv"
        
        inserted_count = 0
        failed_count = 0
        
        for article in unique_news:
            try:
                # Clean data for insertion
                values = (
                    article.get('datetime', ''),
                    article.get('headline', '').replace("'", "''")[:1000],  # Limit length
                    article.get('summary', '').replace("'", "''")[:5000],   # Limit length
                    article.get('source', '')[:200],
                    article.get('url', '')[:500],
                    article.get('categories', '')[:500],
                    article.get('tags', '')[:500],
                    article.get('api_source', ''),
                    file_name
                )
                
                hook.run(insert_sql, parameters=values)
                inserted_count += 1
                
            except Exception as e:
                print(f"Failed to insert article: {str(e)}")
                failed_count += 1
                continue
        
        result_message = f"Successfully inserted {inserted_count} articles, {failed_count} failed"
        print(result_message)
        
        # Push results for notification
        context['task_instance'].xcom_push(key='inserted_count', value=inserted_count)
        context['task_instance'].xcom_push(key='failed_count', value=failed_count)
        
        return result_message
        
    except Exception as e:
        error_message = f"Error inserting articles to Snowflake: {str(e)}"
        print(error_message)
        raise Exception(error_message)

def backup_to_github(**context):
    """Backup data to GitHub (optional, for redundancy)"""
    
    unique_news = context['task_instance'].xcom_pull(task_ids='merge_and_deduplicate_news', key='unique_news') or []
    
    if not unique_news:
        print("No data to backup")
        return "No data to backup"
    
    github_token = os.getenv('GITHUB_TOKEN')
    github_username = 'mouadja02'
    github_repo = 'bitcoin-news-data'
    
    if not github_token:
        print("GitHub token not found, skipping backup")
        return "Skipped - no GitHub token"
    
    # Get current date in GMT+2 (adjust as needed)
    now = datetime.now()
    gmt_plus_2 = now + timedelta(hours=2)
    
    year = gmt_plus_2.year
    month = str(gmt_plus_2.month).zfill(2)
    day = str(gmt_plus_2.day).zfill(2)
    hour = str(gmt_plus_2.hour).zfill(2)
    
    date_string = f"{year}-{month}-{day}_{hour}-00"
    folder_name = f"{day}{month}{year}"
    
    # Create CSV content
    csv_content = "datetime,headline,summary,source,url,categories,tags,api_source\n"
    
    for news in unique_news:
        # Properly escape fields for CSV
        headline = news.get('headline', '').replace('"', '""')
        summary = news.get('summary', '').replace('"', '""')
        source = news.get('source', '').replace(',', '')
        url = news.get('url', '')
        categories = str(news.get('categories', '')).replace('"', '""')
        tags = str(news.get('tags', '')).replace('"', '""')
        api_source = news.get('api_source', '')
        
        row = [
            news.get('datetime', ''),
            f'"{headline}"',
            f'"{summary}"',
            source,
            url,
            f'"{categories}"',
            f'"{tags}"',
            api_source
        ]
        
        csv_content += ','.join(row) + "\n"
    
    # GitHub API setup
    file_path = f'{folder_name}/bitcoin_news_{date_string}.csv'
    url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/{file_path}"
    
    content_base64 = base64.b64encode(csv_content.encode()).decode()
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    
    data = {
        'message': f'Backup: Combined Bitcoin news data - {date_string}',
        'content': content_base64,
    }
    
    try:
        # Check if file exists
        check_response = requests.get(url, headers=headers)
        
        if check_response.status_code == 200:
            # File exists, need to update with SHA
            existing_file = check_response.json()
            data['sha'] = existing_file['sha']
        
        # Create or update file
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"Successfully backed up to GitHub: {file_path}")
        return f"Backed up {len(unique_news)} articles to GitHub"
        
    except Exception as e:
        print(f"Failed to backup to GitHub: {str(e)}")
        return f"Backup failed: {str(e)}"

def send_production_notification(**context):
    """Send enhanced notification with Snowflake insertion results"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Telegram credentials not found, skipping notification")
        return
    
    # Get results from previous tasks
    cryptocompare_count = context['task_instance'].xcom_pull(task_ids='merge_and_deduplicate_news', key='cryptocompare_count') or 0
    finnhub_count = context['task_instance'].xcom_pull(task_ids='merge_and_deduplicate_news', key='finnhub_count') or 0
    total_count = context['task_instance'].xcom_pull(task_ids='merge_and_deduplicate_news', key='total_count') or 0
    inserted_count = context['task_instance'].xcom_pull(task_ids='insert_news_to_snowflake', key='inserted_count') or 0
    failed_count = context['task_instance'].xcom_pull(task_ids='insert_news_to_snowflake', key='failed_count') or 0
    
    # Get current time
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    
    # Create status emoji
    status_emoji = "✅" if failed_count == 0 else "⚠️"
    
    message = f"""{status_emoji} **Bitcoin News Pipeline - Production**

🕐 **Time:** {current_time}

📊 **API Results:**
- CryptoCompare: {cryptocompare_count} articles
- Finnhub: {finnhub_count} articles  
- Total Unique: {total_count} articles

🏔️ **Snowflake Insertion:**
- Successfully inserted: {inserted_count}
- Failed insertions: {failed_count}
- Success rate: {(inserted_count/(inserted_count+failed_count)*100) if (inserted_count+failed_count) > 0 else 0:.1f}%

🌊 **Next Steps:**
- Snowflake Stream will auto-detect new data
- Sentiment analysis will trigger automatically
- F&G Index will be updated in ~15 minutes

🤖 **Pipeline Status:** {'Healthy' if failed_count == 0 else 'Partial Success'}"""
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("Production notification sent successfully")
    except Exception as e:
        print(f"Failed to send notification: {str(e)}")

# Define tasks
fetch_cryptocompare_task = PythonOperator(
    task_id='fetch_cryptocompare_news',
    python_callable=fetch_cryptocompare_news,
    dag=dag,
)

fetch_finnhub_task = PythonOperator(
    task_id='fetch_finnhub_news',
    python_callable=fetch_finnhub_news,
    dag=dag,
)

merge_deduplicate_task = PythonOperator(
    task_id='merge_and_deduplicate_news',
    python_callable=merge_and_deduplicate_news,
    dag=dag,
)

insert_snowflake_task = PythonOperator(
    task_id='insert_news_to_snowflake',
    python_callable=insert_news_to_snowflake,
    dag=dag,
)

backup_github_task = PythonOperator(
    task_id='backup_to_github',
    python_callable=backup_to_github,
    dag=dag,
)

notification_task = PythonOperator(
    task_id='send_production_notification',
    python_callable=send_production_notification,
    dag=dag,
)

# Set task dependencies
[fetch_cryptocompare_task, fetch_finnhub_task] >> merge_deduplicate_task >> insert_snowflake_task >> notification_task