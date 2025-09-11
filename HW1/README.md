# My Daily KakaoTalk Briefing Bot

매일 아침 출근 준비 시간에 스마트폰으로 날씨 앱, 주식 앱, 뉴스 앱을 번갈아 확인하는 반복적인 작업을 자동화하기 위해 기획되었습니다. 사용자가 지정한 지역의 날씨 정보, 관심 있는 주식/암호화폐의 현재 시세 및 등락률, 그리고 주요 IT 기술 뉴스 사이트의 헤드라인을 자동으로 수집합니다. 수집된 정보는 하나의 요약 메시지로 정리되어, 매일 정해진 시간에 카카오톡 "나에게 보내기" API를 통해 사용자에게 전송됩니다. 이 프로젝트는 Python을 기반으로 하며, 다양한 외부 API를 연동하고 백그라운드 스케줄링을 구현하는 경험을 목표로 합니다.

## 📝 프로젝트 기획 배경 (Project Idea)

이 프로젝트는 '만들면 편하겠다'고 생각하지만 막상 직접 코딩하기 번거로워 미루게 되는 대표적인 아이디어에서 출발했습니다. 매일 아침 반복적으로 확인하는 날씨, 주식/코인 시세, IT 뉴스 헤드라인을 하나의 메시지로 취합하여 자동으로 발송하는 봇을 구현함으로써, 개인의 일상 속 비효율을 자동화하는 경험을 제공하고자 했습니다. 특히 API 연동과 스케줄링, 인증 처리는 LLM의 도움을 받을 때 가장 효율적으로 개발할 수 있는 영역이기도 합니다.

이 프로젝트는 Cursor(Gemini CLI)와 같은 LLM 기반 코딩 어시스턴트를 활용하여 개발되었습니다. 아래는 개발 과정에서 사용된 주요 프롬프트 목록입니다.

### 프로젝트 초기 설정

> Initialize a new Python project for a KakaoTalk messaging service. Create a requirements.txt file and add requests, python-dotenv, apscheduler, yfinance, and beautifulsoup4. Also, create a main script kakao_briefing_bot.py, a utility script get_kakao_token.py, and an environment file .env.

### 환경 변수 파일(.env) 설정

> I need to set up the .env file to store my API keys. Please add the following keys with placeholder values: KAKAO_REST_API_KEY, KAKAO_REDIRECT_URI, and OPENWEATHER_API_KEY.

### 카카오 인증 토큰 최초 발급 스크립트 작성

> In get_kakao_token.py, write a script that does two things. First, it should print a Kakao authorization URL using the KAKAO_REST_API_KEY and KAKAO_REDIRECT_URI from the .env file. Second, it should prompt the user to paste the authorization code from the redirected URL. Once the code is entered, the script must exchange it for an access token and a refresh token by making a POST request to kauth.kakao.com. Finally, it should save these tokens into a new file named kakao_token.json.

### 카카오 토큰 관리 및 메시지 발송 모듈 구현

> Now, let's create a class or a set of functions in kakao_briefing_bot.py to handle Kakao API interactions.
> 
> A function load_tokens() to read the tokens from kakao_token.json.
> 
> A function refresh_tokens(refresh_token) that uses the refresh token to get a new access token from Kakao's auth server and updates kakao_token.json.
> 
> A main function send_kakao_message(text) that: a. Loads the tokens. b. Checks if the access token needs refreshing. If so, it calls refresh_tokens. c. Sends the provided text to me using the Kakao Talk "Send to Me" API (/v2/api/talk/memo/default/send). It should format the request correctly as a text template object.

### 날씨 정보 기능 구현

> In kakao_briefing_bot.py, write a Python function called get_weather_info. It should take a city name (e.g., "Yongin") as an argument, fetch the current weather from the OpenWeatherMap API using the requests library and my OPENWEATHER_API_KEY, and return it as a formatted string.

### 금융 정보 기능 구현

> Next, create a function get_financial_info. This function should use the yfinance library to get the current price and percentage change for key tickers like the KOSPI index (^KS11) and Bitcoin (BTC-USD). It should return a formatted string summarizing this information.

### 뉴스 헤드라인 스크래핑 기능 구현

> I want to get the top 5 headlines from a Korean IT news site like 'CIO Korea'. Write a function get_tech_news_headlines that uses requests and BeautifulSoup4 to scrape the main page of ciokorea.com and returns a list of the top 5 article titles.

### 모든 기능 통합 및 스케줄링

> Now, create the main execution logic.
> 
> Create a function run_daily_briefing that calls get_weather_info, get_financial_info, and get_tech_news_headlines.
> 
> It should combine all the returned strings into a single, well-formatted briefing message.
> 
> Finally, it should pass this message to the send_kakao_message function to send the alert.
> 
> Use the apscheduler library to schedule run_daily_briefing to execute every morning at 8:00 AM. The script should start the scheduler and keep running.

---

매일 아침 8시에 날씨, 금융 정보, 기술 뉴스를 카카오톡 "나에게 보내기" API를 통해 전송하는 자동화 봇입니다.

## 기능

- 🌤️ **날씨 정보**: OpenWeatherMap API를 통한 현재 날씨 (온도, 체감온도, 습도, 날씨 상태)
- 📈 **금융 정보**: yfinance를 통한 주식 및 암호화폐 가격 정보 (KOSPI, BTC-USD, ETH-USD, AAPL)
- 📰 **기술 뉴스**: CIO Korea에서 상위 5개 기술 뉴스 헤드라인 스크래핑
- ⏰ **자동 스케줄링**: 매일 오전 10시 45분에 자동으로 브리핑 전송
- 🔐 **토큰 관리**: 자동 토큰 갱신 및 안전한 인증 관리

## 설치 및 설정

### 1. 가상환경 생성 및 활성화

#### Windows (PowerShell)
```powershell
# 가상환경 생성
python -m venv kakao_bot_env

# 가상환경 활성화
.\kakao_bot_env\Scripts\Activate.ps1

# 가상환경 비활성화 (필요시)
deactivate
```

#### Windows (Command Prompt)
```cmd
# 가상환경 생성
python -m venv kakao_bot_env

# 가상환경 활성화
kakao_bot_env\Scripts\activate.bat

# 가상환경 비활성화 (필요시)
deactivate
```

#### macOS/Linux
```bash
# 가상환경 생성
python3 -m venv kakao_bot_env

# 가상환경 활성화
source kakao_bot_env/bin/activate

# 가상환경 비활성화 (필요시)
deactivate
```

### 2. 의존성 설치

가상환경이 활성화된 상태에서:
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

1. `env_example.txt` 파일을 `.env`로 복사합니다:
   ```bash
   # Windows
   copy env_example.txt .env
   
   # macOS/Linux
   cp env_example.txt .env
   ```

2. `.env` 파일을 열어서 다음 정보를 입력합니다:
   ```
   KAKAO_REST_API_KEY=your_kakao_rest_api_key_here
   KAKAO_REDIRECT_URI=https://localhost:3000
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   CITY_NAME=Yongin
   ```

### 4. API 키 획득 방법

#### 카카오 REST API 키
1. [카카오 개발자 사이트](https://developers.kakao.com/) 접속
2. 애플리케이션 등록
3. 플랫폼 설정에서 Web 플랫폼 추가 (리다이렉트 URI: `https://localhost:3000`)
4. REST API 키를 복사하여 `KAKAO_REST_API_KEY`에 입력

#### OpenWeatherMap API 키
1. [OpenWeatherMap](https://openweathermap.org/api) 회원가입
2. API 키 생성
3. 받은 키를 `OPENWEATHER_API_KEY`에 입력

### 5. 카카오 인증 토큰 발급

**가상환경이 활성화된 상태에서 최초 한 번만 실행**:
```bash
python get_kakao_token.py
```

이 스크립트는:
1. 카카오 인증 URL을 출력합니다
2. 브라우저에서 URL을 열고 카카오 계정으로 로그인합니다
3. 인증 코드를 입력하면 액세스 토큰과 리프레시 토큰을 발급받습니다
4. `kakao_token.json` 파일에 토큰을 저장합니다

### 6. 봇 실행

가상환경이 활성화된 상태에서:
```bash
python kakao_briefing_bot.py
```

#### 테스트 실행
```bash
# 간단한 테스트 메시지 전송
python kakao_briefing_bot.py test

# 실제 브리핑 테스트 (날씨, 금융, 뉴스 포함)
python kakao_briefing_bot.py briefing
```

## 프로젝트 구조

```
HW1/
├── kakao_briefing_bot.py    # 메인 봇 스크립트
├── get_kakao_token.py       # 카카오 인증 토큰 발급 스크립트
├── requirements.txt         # Python 의존성
├── env_example.txt         # 환경 변수 예시 파일
├── kakao_token.json        # 카카오 토큰 저장 파일 (자동 생성)
├── kakao_bot_env/          # 가상환경 폴더 (자동 생성)
│   ├── Scripts/            # Windows 실행 파일들
│   ├── Lib/                # 설치된 패키지들
│   └── pyvenv.cfg          # 가상환경 설정
└── README.md              # 프로젝트 문서
```

## 주요 함수

### kakao_briefing_bot.py
- `load_tokens()`: kakao_token.json에서 토큰 로드
- `refresh_tokens(refresh_token)`: 리프레시 토큰으로 새 액세스 토큰 발급
- `send_kakao_message(text)`: 카카오톡 "나에게 보내기" API로 메시지 전송
- `get_weather_info(city)`: 도시별 현재 날씨 정보 조회
- `get_financial_info()`: 주식 및 암호화폐 가격 정보 조회
- `get_tech_news_headlines()`: CIO Korea 헤드라인 스크래핑
- `run_daily_briefing()`: 통합 브리핑 메시지 생성 및 전송

### get_kakao_token.py
- `get_authorization_url()`: 카카오 인증 URL 생성
- `exchange_code_for_token(authorization_code)`: 인증 코드를 토큰으로 교환

## 사용된 라이브러리

- `requests`: HTTP 요청
- `python-dotenv`: 환경 변수 관리
- `apscheduler`: 작업 스케줄링
- `yfinance`: 금융 데이터 조회
- `beautifulsoup4`: 웹 스크래핑

## 카카오 API 사용법

### 1. 카카오 개발자 사이트 설정
1. [카카오 개발자 사이트](https://developers.kakao.com/)에서 애플리케이션 등록
2. 플랫폼 설정에서 Web 플랫폼 추가
3. 리다이렉트 URI 설정: `https://localhost:3000`
4. 동의항목 설정에서 "카카오톡 메시지 전송" 권한 활성화

### 2. 토큰 관리
- 액세스 토큰은 12시간 후 만료됩니다
- 리프레시 토큰은 2개월 후 만료됩니다
- 봇이 자동으로 토큰을 갱신합니다
- 토큰이 만료되면 `get_kakao_token.py`를 다시 실행하세요

## GitHub 연동

### Git 저장소 초기화 및 GitHub 연동

```bash
# Git 저장소 초기화
git init

# .gitignore 파일 생성 (중요!)
echo ".env" > .gitignore
echo "kakao_token.json" >> .gitignore
echo "kakao_bot_env/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".DS_Store" >> .gitignore
echo "*.log" >> .gitignore

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: KakaoTalk Daily Briefing Bot setup with virtual environment"

# GitHub 저장소 연결 (your-username과 your-repo-name을 실제 값으로 변경)
git remote add origin https://github.com/your-username/your-repo-name.git

# 메인 브랜치로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

## 주의사항

- `.env` 파일과 `kakao_token.json` 파일은 절대 GitHub에 업로드하지 마세요 (보안상 중요)
- `kakao_bot_env/` 가상환경 폴더도 GitHub에 업로드하지 마세요 (용량이 크고 불필요)
- API 키는 안전하게 보관하세요
- 봇을 실행하기 전에 반드시 가상환경을 활성화하세요
- 봇이 실행 중일 때는 터미널을 종료하지 마세요
- 카카오 API 사용량 제한을 확인하세요
- 가상환경을 사용하면 시스템 Python과 분리되어 의존성 충돌을 방지할 수 있습니다

## 문제 해결

- **가상환경 활성화 실패**: PowerShell 실행 정책 문제일 수 있습니다. `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` 실행 후 재시도
- **패키지 설치 실패**: 가상환경이 활성화되었는지 확인하세요 (`pip list`로 확인)
- **토큰 발급 실패**: 카카오 개발자 사이트에서 애플리케이션 설정을 확인하세요
- **메시지 전송 실패**: 토큰이 만료되었을 수 있습니다. `get_kakao_token.py`를 다시 실행하세요
- **날씨 정보 없음**: OpenWeatherMap API 키와 도시 이름을 확인하세요
- **금융 정보 없음**: 인터넷 연결을 확인하세요
- **뉴스 스크래핑 실패**: CIO Korea 사이트 접근을 확인하세요
- **모듈을 찾을 수 없음**: 가상환경이 활성화되지 않았거나 패키지가 설치되지 않았습니다

## 라이선스

이 프로젝트는 개인 사용을 위한 교육 목적으로 제작되었습니다.