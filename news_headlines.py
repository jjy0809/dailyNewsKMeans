import os
import json
import time
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

data_dir = r'C:\Users\happy\Desktop\학교\고등학교\2학년\일일 뉴스 헤드라인\data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(options=chrome_options)

def news_fetch(url, max_clicks=5):
    driver.get(url)
    time.sleep(2)
    for _ in range(max_clicks):
        try:
            more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "button_rankingnews_more"))
            )
            more_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"No more '더보기' button or error occurred: {e}")
            break
    headlines = []
    elements = driver.find_elements(By.CLASS_NAME, "list_title")
    for element in elements:
        raw_title = element.text.strip()
        if raw_title:
            clean_title = re.sub(r'[^\w\s]', ' ', raw_title)
            clean_title = re.sub(r'\s+', ' ', clean_title).strip()
            if clean_title:
                headlines.append(clean_title)
    print(f"수집된 헤드라인 수: {len(headlines)}")
    return headlines

def fetch_daily_news(date, max_clicks=5):
    all_headlines = []
    popular_view_url = f"https://news.naver.com/main/ranking/popularDay.naver?date={date}"
    print(f"많이 본 뉴스: {date}")
    all_headlines.extend(news_fetch(popular_view_url, max_clicks))
    popular_comment_url = f"https://news.naver.com/main/ranking/popularMemo.naver?date={date}"
    print(f"댓글 많은 뉴스: {date}")
    all_headlines.extend(news_fetch(popular_comment_url, max_clicks))
    return all_headlines

def fetch_news_by_date_range(start_date, end_date):
    news_data = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m%d')
        daily_headlines = fetch_daily_news(date_str)
        news_data[date_str] = daily_headlines
        current_date += timedelta(days=1)
    return news_data

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

start_date = datetime(2024, 12, 1)
end_date = datetime(2024, 12, 7)

news_data = fetch_news_by_date_range(start_date, end_date)

output_file = os.path.join(data_dir, 'news.json')
save_to_json(news_data, output_file)

driver.quit()

print(f"저장 완료")
