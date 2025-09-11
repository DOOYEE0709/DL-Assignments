#!/usr/bin/env python3
"""
Daily KakaoTalk Briefing Bot
매일 아침 8시에 날씨, 금융 정보, 기술 뉴스를 카카오톡으로 전송하는 봇
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

import requests
import yfinance as yf
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 환경 변수
KAKAO_REST_API_KEY = os.getenv('KAKAO_REST_API_KEY')
KAKAO_REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URI')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
CITY_NAME = os.getenv('CITY_NAME', 'Yongin')  # 기본값: 용인

# 카카오 API 엔드포인트
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_MESSAGE_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

def load_tokens() -> Dict[str, str]:
    """
    kakao_token.json 파일에서 토큰을 로드합니다.
    
    Returns:
        Dict[str, str]: access_token과 refresh_token을 포함한 딕셔너리
    """
    try:
        with open('kakao_token.json', 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        return tokens
    except FileNotFoundError:
        logger.error("kakao_token.json 파일을 찾을 수 없습니다. get_kakao_token.py를 먼저 실행하세요.")
        return {}
    except json.JSONDecodeError:
        logger.error("kakao_token.json 파일 형식이 올바르지 않습니다.")
        return {}

def refresh_tokens(refresh_token: str) -> bool:
    """
    리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.
    
    Args:
        refresh_token (str): 리프레시 토큰
        
    Returns:
        bool: 토큰 갱신 성공 여부
    """
    try:
        data = {
            'grant_type': 'refresh_token',
            'client_id': KAKAO_REST_API_KEY,
            'refresh_token': refresh_token
        }
        
        response = requests.post(KAKAO_AUTH_URL, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # 새로운 토큰으로 파일 업데이트
        new_tokens = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token', refresh_token)  # 새 리프레시 토큰이 없으면 기존 것 사용
        }
        
        with open('kakao_token.json', 'w', encoding='utf-8') as f:
            json.dump(new_tokens, f, ensure_ascii=False, indent=2)
        
        logger.info("토큰이 성공적으로 갱신되었습니다.")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"토큰 갱신 실패: {e}")
        return False
    except Exception as e:
        logger.error(f"토큰 갱신 중 오류: {e}")
        return False

def send_kakao_message(text: str) -> bool:
    """
    카카오톡 "나에게 보내기" API를 사용하여 메시지를 전송합니다.
    
    Args:
        text (str): 전송할 메시지 텍스트
        
    Returns:
        bool: 메시지 전송 성공 여부
    """
    try:
        # 토큰 로드
        tokens = load_tokens()
        if not tokens:
            return False
        
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        
        if not access_token:
            logger.error("액세스 토큰을 찾을 수 없습니다.")
            return False
        
        # 메시지 템플릿 구성
        template = {
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": "https://developers.kakao.com",
                "mobile_web_url": "https://developers.kakao.com"
            }
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'template_object': json.dumps(template, ensure_ascii=False)
        }
        
        # 메시지 전송 시도
        response = requests.post(KAKAO_MESSAGE_URL, headers=headers, data=data)
        
        # 토큰 만료 시 갱신 후 재시도
        if response.status_code == 401:
            logger.info("토큰이 만료되었습니다. 토큰을 갱신합니다.")
            if refresh_tokens(refresh_token):
                # 갱신된 토큰으로 재시도
                new_tokens = load_tokens()
                headers['Authorization'] = f'Bearer {new_tokens["access_token"]}'
                response = requests.post(KAKAO_MESSAGE_URL, headers=headers, data=data)
            else:
                logger.error("토큰 갱신에 실패했습니다.")
                return False
        
        response.raise_for_status()
        logger.info("카카오톡 메시지 전송 성공")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"카카오톡 메시지 전송 실패: {e}")
        return False
    except Exception as e:
        logger.error(f"메시지 전송 중 오류: {e}")
        return False

def get_weather_info(city: str) -> str:
    """
    OpenWeatherMap API를 사용하여 현재 날씨 정보를 가져옵니다.
    
    Args:
        city (str): 도시 이름
        
    Returns:
        str: 포맷된 날씨 정보 문자열
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',
            'lang': 'kr'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        temperature = data['main']['temp']
        feels_like = data['main']['feels_like']
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        
        weather_info = f"🌤️ {city} 날씨\n"
        weather_info += f"온도: {temperature:.1f}°C (체감 {feels_like:.1f}°C)\n"
        weather_info += f"상태: {description}\n"
        weather_info += f"습도: {humidity}%\n"
        
        return weather_info
        
    except requests.exceptions.RequestException as e:
        logger.error(f"날씨 API 요청 실패: {e}")
        return f"❌ {city} 날씨 정보를 가져올 수 없습니다."
    except KeyError as e:
        logger.error(f"날씨 데이터 파싱 오류: {e}")
        return f"❌ 날씨 데이터를 처리할 수 없습니다."

def get_financial_info() -> str:
    """
    yfinance를 사용하여 주식 및 암호화폐 정보를 가져옵니다.
    
    Returns:
        str: 포맷된 금융 정보 문자열
    """
    try:
        financial_info = "📈 금융 정보\n"
        
        # 한국 주식 및 암호화폐 티커
        tickers = ['^KS11', 'BTC-USD', 'ETH-USD', 'AAPL']  # KOSPI, 비트코인, 이더리움, 애플
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="7d")  # 일주일 데이터로 충분한 데이터 확보
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2]
                    change_percent = ((current_price - previous_price) / previous_price) * 100
                    
                    # 티커별 표시 기호 설정
                    if ticker == '^KS11':
                        symbol = "🇰🇷"
                        price_format = f"{current_price:.1f}"
                    elif 'BTC' in ticker:
                        symbol = "₿"
                        price_format = f"${current_price:.2f}"
                    elif 'ETH' in ticker:
                        symbol = "Ξ"
                        price_format = f"${current_price:.2f}"
                    else:
                        symbol = "📊"
                        price_format = f"${current_price:.2f}"
                    
                    change_emoji = "📈" if change_percent >= 0 else "📉"
                    
                    financial_info += f"{symbol} {ticker}: {price_format} ({change_emoji} {change_percent:+.2f}%)\n"
                    
                elif not hist.empty and len(hist) == 1:
                    # 데이터가 1개만 있는 경우 (현재 가격만 표시)
                    current_price = hist['Close'].iloc[-1]
                    
                    if ticker == '^KS11':
                        symbol = "🇰🇷"
                        price_format = f"{current_price:.1f}"
                    elif 'BTC' in ticker:
                        symbol = "₿"
                        price_format = f"${current_price:.2f}"
                    elif 'ETH' in ticker:
                        symbol = "Ξ"
                        price_format = f"${current_price:.2f}"
                    else:
                        symbol = "📊"
                        price_format = f"${current_price:.2f}"
                    
                    financial_info += f"{symbol} {ticker}: {price_format} (변동률 없음)\n"
                    
            except Exception as e:
                logger.error(f"{ticker} 정보 가져오기 실패: {e}")
                financial_info += f"❌ {ticker}: 정보 없음\n"
        
        return financial_info
        
    except Exception as e:
        logger.error(f"금융 정보 가져오기 실패: {e}")
        return "❌ 금융 정보를 가져올 수 없습니다."

def get_tech_news_headlines() -> str:
    """
    CIO Korea에서 상위 5개 기술 뉴스 헤드라인을 스크래핑합니다.
    
    Returns:
        str: 포맷된 뉴스 헤드라인 문자열
    """
    try:
        url = "https://www.ciokorea.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # CIO Korea의 기사 링크 찾기 (사이트 구조에 따라 조정 필요)
        news_links = soup.find_all('a', href=True)
        
        news_info = "📰 기술 뉴스 (CIO Korea)\n"
        
        # 기사 제목과 링크 추출
        article_count = 0
        for link in news_links:
            if link.get('href') and ('/news/' in link.get('href') or '/article/' in link.get('href')):
                title = link.get_text().strip()
                href = link.get('href')
                
                if title and len(title) > 10 and article_count < 5:
                    # 상대 URL을 절대 URL로 변환
                    if href.startswith('/'):
                        href = f"https://www.ciokorea.com{href}"
                    
                    article_count += 1
                    news_info += f"{article_count}. {title}\n"
                    news_info += f"   링크: {href}\n"
        
        if article_count == 0:
            news_info += "❌ 뉴스를 찾을 수 없습니다.\n"
        
        return news_info
        
    except requests.exceptions.RequestException as e:
        logger.error(f"뉴스 스크래핑 요청 실패: {e}")
        return "❌ 기술 뉴스를 가져올 수 없습니다."
    except Exception as e:
        logger.error(f"뉴스 스크래핑 실패: {e}")
        return "❌ 뉴스 데이터를 처리할 수 없습니다."

def run_daily_briefing():
    """
    일일 브리핑을 실행하고 카카오톡으로 전송합니다.
    """
    try:
        logger.info("일일 브리핑 실행 시작")
        
        # 각 정보 수집
        weather = get_weather_info(CITY_NAME)
        financial = get_financial_info()
        news = get_tech_news_headlines()
        
        # 메시지 구성
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        
        message = f"🌅 일일 브리핑 - {current_time}\n\n"
        message += weather + "\n"
        message += financial + "\n"
        message += news
        
        # 카카오톡으로 전송
        if send_kakao_message(message):
            logger.info("일일 브리핑 전송 완료")
        else:
            logger.error("일일 브리핑 전송 실패")
        
    except Exception as e:
        logger.error(f"일일 브리핑 실행 중 오류: {e}")

async def main():
    """
    메인 함수 - 스케줄러 설정 및 실행
    """
    # 환경 변수 검증
    if not all([KAKAO_REST_API_KEY, KAKAO_REDIRECT_URI, OPENWEATHER_API_KEY]):
        logger.error("필수 환경 변수가 설정되지 않았습니다.")
        logger.error("KAKAO_REST_API_KEY, KAKAO_REDIRECT_URI, OPENWEATHER_API_KEY를 확인하세요.")
        return
    
    # 토큰 파일 존재 확인
    if not os.path.exists('kakao_token.json'):
        logger.error("kakao_token.json 파일이 없습니다.")
        logger.error("먼저 get_kakao_token.py를 실행하여 인증을 완료하세요.")
        return
    
    # 스케줄러 설정
    scheduler = AsyncIOScheduler()
    
    # 매일 오전 8시에 실행
    scheduler.add_job(
        run_daily_briefing,
        trigger=CronTrigger(hour=8, minute=00),
        id='daily_briefing',
        name='Daily Briefing',
        replace_existing=True
    )
    
    # 스케줄러 시작
    scheduler.start()
    logger.info("스케줄러가 시작되었습니다. 매일 오전 8시에 브리핑을 전송합니다.")
    
    # 봇 실행 상태 유지
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("봇이 종료됩니다.")
        scheduler.shutdown()

def test_message():
    """
    테스트용 메시지 전송 함수
    """
    print("🧪 테스트 메시지를 전송합니다...")
    
    # 테스트 메시지 구성
    current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
    test_message = f"🧪 테스트 메시지 - {current_time}\n\n"
    test_message += "✅ 카카오톡 브리핑 봇이 정상적으로 작동합니다!\n"
    test_message += "🌤️ 날씨 정보 테스트\n"
    test_message += "📈 금융 정보 테스트\n"
    test_message += "📰 뉴스 정보 테스트\n\n"
    test_message += "이 메시지가 보인다면 봇 설정이 완료되었습니다! 🎉"
    
    # 메시지 전송
    if send_kakao_message(test_message):
        print("✅ 테스트 메시지 전송 성공!")
    else:
        print("❌ 테스트 메시지 전송 실패!")

def test_full_briefing():
    """
    실제 브리핑 테스트 함수 (날씨, 금융, 뉴스 포함)
    """
    print("🧪 실제 브리핑을 테스트합니다...")
    run_daily_briefing()

if __name__ == "__main__":
    import sys
    
    # 명령행 인수 확인
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # 간단한 테스트 메시지
            test_message()
        elif sys.argv[1] == "briefing":
            # 실제 브리핑 테스트 (날씨, 금융, 뉴스 포함)
            test_full_briefing()
        else:
            print("사용법:")
            print("  python kakao_briefing_bot.py test      # 간단한 테스트 메시지")
            print("  python kakao_briefing_bot.py briefing  # 실제 브리핑 테스트")
            print("  python kakao_briefing_bot.py           # 일반 실행 (스케줄러)")
    else:
        # 일반 실행 모드
        asyncio.run(main())
