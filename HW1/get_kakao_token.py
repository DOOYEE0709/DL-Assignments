#!/usr/bin/env python3
"""
카카오 인증 토큰 발급 스크립트
최초 한 번만 실행하여 카카오 API 인증을 받고 토큰을 발급받습니다.
"""

import os
import json
import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 환경 변수
KAKAO_REST_API_KEY = os.getenv('KAKAO_REST_API_KEY')
KAKAO_REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URI')

def get_authorization_url():
    """
    카카오 인증 URL을 생성하고 출력합니다.
    """
    if not KAKAO_REST_API_KEY or not KAKAO_REDIRECT_URI:
        print("❌ 환경 변수가 설정되지 않았습니다.")
        print("KAKAO_REST_API_KEY와 KAKAO_REDIRECT_URI를 .env 파일에 설정하세요.")
        return None
    
    # 카카오 인증 URL 생성
    auth_url = (
        f"https://kauth.kakao.com/oauth/authorize?"
        f"client_id={KAKAO_REST_API_KEY}&"
        f"redirect_uri={KAKAO_REDIRECT_URI}&"
        f"response_type=code"
    )
    
    print("🔗 카카오 인증 URL:")
    print(auth_url)
    print("\n📋 다음 단계:")
    print("1. 위 URL을 브라우저에서 열어주세요")
    print("2. 카카오 계정으로 로그인하세요")
    print("3. 권한을 허용하세요")
    print("4. 리다이렉트된 URL에서 'code=' 뒤의 인증 코드를 복사하세요")
    print("5. 아래에 인증 코드를 붙여넣으세요")
    
    return auth_url

def exchange_code_for_token(authorization_code):
    """
    인증 코드를 액세스 토큰과 리프레시 토큰으로 교환합니다.
    
    Args:
        authorization_code (str): 카카오에서 받은 인증 코드
        
    Returns:
        bool: 토큰 발급 성공 여부
    """
    try:
        # 토큰 교환 요청
        data = {
            'grant_type': 'authorization_code',
            'client_id': KAKAO_REST_API_KEY,
            'redirect_uri': KAKAO_REDIRECT_URI,
            'code': authorization_code
        }
        
        response = requests.post('https://kauth.kakao.com/oauth/token', data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # 토큰을 파일에 저장
        tokens = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token']
        }
        
        with open('kakao_token.json', 'w', encoding='utf-8') as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)
        
        print("✅ 토큰이 성공적으로 발급되고 저장되었습니다!")
        print("📁 kakao_token.json 파일이 생성되었습니다.")
        print("🚀 이제 kakao_briefing_bot.py를 실행할 수 있습니다.")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 토큰 발급 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"응답 내용: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def main():
    """
    메인 함수
    """
    print("🤖 카카오톡 브리핑 봇 토큰 발급 도구")
    print("=" * 50)
    
    # 환경 변수 확인
    if not KAKAO_REST_API_KEY or not KAKAO_REDIRECT_URI:
        print("❌ .env 파일에 필요한 환경 변수가 설정되지 않았습니다.")
        print("다음 변수들을 확인하세요:")
        print("- KAKAO_REST_API_KEY")
        print("- KAKAO_REDIRECT_URI")
        return
    
    # 인증 URL 생성 및 출력
    auth_url = get_authorization_url()
    if not auth_url:
        return
    
    # 사용자로부터 인증 코드 입력 받기
    print("\n" + "=" * 50)
    authorization_code = input("인증 코드를 입력하세요: ").strip()
    
    if not authorization_code:
        print("❌ 인증 코드가 입력되지 않았습니다.")
        return
    
    # 토큰 교환
    print("\n🔄 토큰을 발급받는 중...")
    if exchange_code_for_token(authorization_code):
        print("\n🎉 설정이 완료되었습니다!")
        print("이제 kakao_briefing_bot.py를 실행하여 봇을 시작할 수 있습니다.")
    else:
        print("\n❌ 토큰 발급에 실패했습니다.")
        print("인증 코드를 다시 확인하고 재시도해주세요.")

if __name__ == "__main__":
    main()
