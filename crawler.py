import requests
from bs4 import BeautifulSoup
import os
import json

# 1. 대상 대학 설정 (대학명, 게시판 URL, 데이터 추출용 CSS 선택자)
UNIVERSITIES = [
    {
        "name": "강릉원주대",
        "url": "https://www.gwnu.ac.kr/kr/7924/subview.do",
        "selector": "tr:not(.notice) td.td-subject a", # 공지(notice) 제외한 일반글
        "base_url": "https://www.gwnu.ac.kr"
    },
    {
        "name": "가톨릭관동대",
        "url": "https://www.cku.ac.kr/cku_kr/5787/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGY2t1X2tyJTJGMTIwMiUyRmFydGNsTGlzdC5kbyUzRmJic0NsU2VxJTNEMTU4NCUyNmJic09wZW5XcmRTZXElM0QlMjZpc1ZpZXdNaW5lJTNEZmFsc2UlMjZzcmNoQ29sdW1uJTNEc2olMjZzcmNoV3JkJTNEJTI2",
        "selector": "tr:not(.notice) td.td-subject a",
        "base_url": "https://www.cku.ac.kr"
    },
    {
        "name": "강릉영동대",
        "url": "https://www.gyu.ac.kr/gyu/selectBbsNttList.do?bbsNo=210&key=387",
        "selector": "tr:not(.notice) td.td-subject a",
        "base_url": "https://www.gyc.ac.kr"
    }
]

DB_FILE = "last_posts.json"

def load_last_posts():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_last_posts(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def send_telegram(message):
    # 보안을 위해 토큰과 ID는 GitHub Secrets 사용을 권장합니다.
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("토큰 또는 채팅 ID가 설정되지 않았습니다.")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": message}
    requests.get(url, params=params)

def crawl():
    last_posts = load_last_posts()
    new_data = last_posts.copy()

    for univ in UNIVERSITIES:
        try:
            response = requests.get(univ["url"], timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 최신글 하나 추출
            post_element = soup.select_one(univ["selector"])
            if not post_element:
                continue

            title = post_element.get_text(strip=True)
            link = univ["base_url"] + post_element['href']
            
            # 이전 저장된 제목과 비교
            if last_posts.get(univ["name"]) != title:
                print(f"[{univ['name']}] 새로운 공고 발견!")
                message = f"📢 [{univ['name']}] 새 채용공고\n제목: {title}\n링크: {link}"
                send_telegram(message)
                new_data[univ["name"]] = title
            else:
                print(f"[{univ['name']}] 새로운 공고 없음")
                
        except Exception as e:
            print(f"{univ['name']} 크롤링 중 오류 발생: {e}")

    save_last_posts(new_data)

if __name__ == "__main__":
    crawl()
