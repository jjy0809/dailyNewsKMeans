import os
import json
import time
import re  # 정규식을 사용하여 특수기호 제거
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait  # 명시적 대기를 위한 모듈
from selenium.webdriver.support import expected_conditions as EC  # 대기 조건 설정

# 데이터 저장 디렉토리 설정
data_dir = r'C:\Users\happy\Desktop\학교\고등학교\2학년\일일 뉴스 헤드라인\data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Chrome WebDriver 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저를 표시하지 않음
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920x1080")  # 화면 크기를 지정

# WebDriver 생성
driver = webdriver.Chrome(options=chrome_options)

# 특정 URL의 뉴스 헤드라인 수집 함수
def fetch_news_from_url(url, max_clicks=5):
    driver.get(url)  # URL 접속
    time.sleep(2)  # 페이지 로드 대기
    
    # '다른 언론사 랭킹 더보기' 버튼 클릭 (최대 max_clicks번)
    for _ in range(max_clicks):
        try:
            # 명시적 대기를 사용하여 버튼이 나타날 때까지 기다림
            more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "button_rankingnews_more"))
            )
            more_button.click()  # 버튼 클릭
            time.sleep(2)  # 로딩 대기
        except Exception as e:
            print(f"No more '더보기' button or error occurred: {e}")
            break
    
    # 뉴스 제목 수집
    headlines = []
    elements = driver.find_elements(By.CLASS_NAME, "list_title")
    for element in elements:
        raw_title = element.text.strip()
        if raw_title:  # 빈 문자열인지 확인
            # 특수기호 제거 및 공백 하나로 치환
            clean_title = re.sub(r'[^\w\s]', ' ', raw_title)  # 특수기호 제거
            clean_title = re.sub(r'\s+', ' ', clean_title).strip()  # 공백을 하나로 치환
            if clean_title:  # 최종적으로 빈 문자열이 아닌 경우만 추가
                headlines.append(clean_title)
    
    print(f"수집된 헤드라인 수: {len(headlines)}")
    return headlines

# 특정 날짜의 뉴스 헤드라인 수집 함수 (많이 본 뉴스 + 댓글 많은 뉴스)
def fetch_daily_news(date, max_clicks=5):
    all_headlines = []  # 해당 날짜의 모든 헤드라인 저장
    
    # 많이 본 뉴스 URL
    popular_view_url = f"https://news.naver.com/main/ranking/popularDay.naver?date={date}"
    print(f"Fetching '많이 본 뉴스' for date: {date}")
    all_headlines.extend(fetch_news_from_url(popular_view_url, max_clicks))  # 많이 본 뉴스 추가
    
    # 댓글 많은 뉴스 URL
    popular_comment_url = f"https://news.naver.com/main/ranking/popularMemo.naver?date={date}"
    print(f"Fetching '댓글 많은 뉴스' for date: {date}")
    all_headlines.extend(fetch_news_from_url(popular_comment_url, max_clicks))  # 댓글 많은 뉴스 추가
    
    return all_headlines

# 날짜 범위 내의 뉴스 데이터 수집 함수
def fetch_news_by_date_range(start_date, end_date):
    news_data = {}
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m%d')  # 날짜를 YYYYMMDD 형식으로 변환
        daily_headlines = fetch_daily_news(date_str)  # 해당 날짜의 모든 뉴스 수집
        news_data[date_str] = daily_headlines  # 날짜별 헤드라인 저장
        
        current_date += timedelta(days=1)  # 다음 날짜로 이동
    
    return news_data

# JSON 파일로 저장 함수
def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 메인 실행 부분
start_date = datetime(2024, 12, 1)  # 시작 날짜 (2024년 12월 1일)
end_date = datetime(2024, 12, 7)   # 종료 날짜 (2024년 12월 7일)

news_data = fetch_news_by_date_range(start_date, end_date)  # 뉴스 데이터 수집

output_file = os.path.join(data_dir, 'news.json')  # JSON 파일 경로 설정
save_to_json(news_data, output_file)  # JSON 파일로 저장

driver.quit()  # WebDriver 종료

print(f"뉴스 데이터가 '{output_file}'에 저장되었습니다.")