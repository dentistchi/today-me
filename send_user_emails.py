#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자에게 실제 이메일 발송
WeeklyEmailSystem + RealEmailSender 통합
"""

from weekly_email_system import WeeklyEmailSystem
from real_email_sender import RealEmailSender
from datetime import datetime
import os
import sys

# .env 파일 로드
def load_env():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 환경 변수 로드
load_env()


def send_user_emails(
    user_email: str,
    user_name: str,
    start_date: datetime,
    analysis_results: dict = None,
    retest_link: str = "https://example.com/retest",
    pdf_report_path: str = None
):
    """
    사용자에게 6개 이메일 실제 발송
    
    Args:
        user_email: 사용자 이메일
        user_name: 사용자 이름
        start_date: 시작 날짜
        analysis_results: 분석 결과
        retest_link: 재검사 링크
        pdf_report_path: PDF 보고서 경로
    """
    
    print("="*70)
    print("사용자 이메일 발송 시작")
    print("="*70)
    print(f"사용자: {user_name} ({user_email})")
    print(f"시작일: {start_date.strftime('%Y-%m-%d')}")
    print()
    
    # 1. SMTP 설정 확인
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("❌ 오류: SMTP 설정이 필요합니다.\n")
        print("다음 환경 변수를 설정하세요:")
        print("  export SMTP_HOST=smtp.gmail.com")
        print("  export SMTP_PORT=587")
        print("  export SMTP_USER=your-email@gmail.com")
        print("  export SMTP_PASSWORD=your-app-password")
        print("  export FROM_EMAIL=your-email@gmail.com")
        print()
        print("Gmail 사용 가이드:")
        print("  python real_email_sender.py setup")
        print()
        return False
    
    print("✅ SMTP 설정 확인 완료")
    print(f"   발신자: {os.getenv('FROM_EMAIL', smtp_user)}")
    print()
    
    # 2. 이메일 시스템 생성
    print("📧 이메일 생성 중...")
    email_system = WeeklyEmailSystem(
        user_email=user_email,
        user_name=user_name,
        start_date=start_date,
        analysis_results=analysis_results,
        retest_link=retest_link,
        pdf_report_path=pdf_report_path
    )
    
    # 6개 이메일 생성
    emails = email_system.generate_all_emails()
    print(f"✅ {len(emails)}개 이메일 생성 완료")
    print()
    
    # 3. 이메일 발송
    print("="*70)
    print("이메일 발송 중...")
    print("="*70)
    
    sender = RealEmailSender()
    results = []
    
    for i, email in enumerate(emails, 1):
        print(f"\n[{i}/{len(emails)}] {email['type']}")
        print(f"   제목: {email['subject'][:50]}...")
        print(f"   예약 시각: {email['send_at']}")
        
        result = sender.send_email(
            to_email=email['to'],
            subject=email['subject'],
            html_body=email['body_html'],
            attachments=email.get('attachments', [])
        )
        
        results.append(result)
    
    # 4. 결과 요약
    print()
    print("="*70)
    print("발송 결과 요약")
    print("="*70)
    
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print()
    
    if fail_count > 0:
        print("실패한 이메일:")
        for r in results:
            if not r['success']:
                print(f"  - {r.get('subject', 'Unknown')}: {r.get('error', 'Unknown error')}")
        print()
    
    # 5. JSON 스케줄 저장
    json_path = email_system.export_to_json(f"outputs/sent_schedule_{user_email}.json")
    print(f"📄 발송 기록 저장: {json_path}")
    print()
    
    return success_count == len(results)


def send_test_email_to_user():
    """테스트 이메일 발송 (대화형)"""
    
    print("="*70)
    print("테스트 이메일 발송")
    print("="*70)
    print()
    
    # 사용자 정보 입력
    user_email = input("사용자 이메일 주소: ").strip()
    if not user_email:
        print("이메일 주소가 필요합니다.")
        return False
    
    user_name = input("사용자 이름 (기본값: 테스트사용자): ").strip()
    if not user_name:
        user_name = "테스트사용자"
    
    # 시작 날짜 (기본값: 오늘)
    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    print()
    print(f"✅ 입력 정보:")
    print(f"   이메일: {user_email}")
    print(f"   이름: {user_name}")
    print(f"   시작일: {start_date.strftime('%Y-%m-%d %H:%M')}")
    print()
    
    confirm = input("이메일을 발송하시겠습니까? (y/n): ").strip().lower()
    if confirm != 'y':
        print("취소되었습니다.")
        return False
    
    print()
    
    # 이메일 발송
    success = send_user_emails(
        user_email=user_email,
        user_name=user_name,
        start_date=start_date,
        retest_link="https://example.com/retest"
    )
    
    if success:
        print("🎉 모든 이메일이 성공적으로 발송되었습니다!")
        print(f"   {user_email}의 받은 편지함을 확인하세요.")
    else:
        print("⚠️  일부 이메일 발송에 실패했습니다.")
        print("   로그 파일(email_send_log.txt)을 확인하세요.")
    
    return success


def send_to_specific_user():
    """특정 사용자에게 발송 (코드 방식)"""
    
    # 환경 변수 또는 설정에서 사용자 정보 가져오기
    user_email = os.getenv('USER_EMAIL', 'user@example.com')
    user_name = os.getenv('USER_NAME', '홍길동')
    
    # 분석 결과 (실제로는 데이터베이스에서 가져옴)
    analysis_results = {
        "scores": {"rosenberg": 18},
        "profile_type": "vulnerable",
        "detected_patterns": [
            {"type": "SELF_CRITICISM", "strength": 0.92},
            {"type": "SOCIAL_COMPARISON", "strength": 0.78}
        ],
        "hidden_strengths": [
            {"name": "공감 능력", "description": "타인의 감정을 잘 이해합니다"}
        ]
    }
    
    # 이메일 발송
    success = send_user_emails(
        user_email=user_email,
        user_name=user_name,
        start_date=datetime.now().replace(hour=9, minute=0, second=0, microsecond=0),
        analysis_results=analysis_results,
        retest_link="https://yourapp.com/retest",
        pdf_report_path="outputs/report_user.pdf"  # 실제 PDF 경로
    )
    
    return success


# ==========================================
# CLI 인터페이스
# ==========================================

def main():
    """메인 함수"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            # 대화형 테스트
            send_test_email_to_user()
            
        elif command == "send":
            # 특정 사용자에게 발송
            if len(sys.argv) >= 4:
                email = sys.argv[2]
                name = sys.argv[3]
                send_user_emails(
                    user_email=email,
                    user_name=name,
                    start_date=datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
                )
            else:
                print("사용법: python send_user_emails.py send <email> <name>")
                
        elif command == "setup":
            # SMTP 설정 가이드
            from real_email_sender import setup_gmail_smtp
            setup_gmail_smtp()
            
        else:
            print("알 수 없는 명령어입니다.")
            print_usage()
    else:
        print_usage()


def print_usage():
    """사용법 출력"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              사용자 이메일 발송 시스템                               ║
╚══════════════════════════════════════════════════════════════════════╝

사용법:
  python send_user_emails.py setup                  # SMTP 설정 가이드
  python send_user_emails.py test                   # 대화형 테스트 발송
  python send_user_emails.py send <email> <name>    # 특정 사용자에게 발송

예제:
  # 1. SMTP 설정 가이드 보기
  python send_user_emails.py setup

  # 2. 환경 변수 설정
  export SMTP_HOST=smtp.gmail.com
  export SMTP_PORT=587
  export SMTP_USER=your-email@gmail.com
  export SMTP_PASSWORD=your-app-password
  export FROM_EMAIL=your-email@gmail.com

  # 3. 테스트 발송
  python send_user_emails.py test

  # 4. 특정 사용자에게 발송
  python send_user_emails.py send user@example.com "홍길동"

Python 코드에서 사용:
  from send_user_emails import send_user_emails
  from datetime import datetime
  
  send_user_emails(
      user_email='user@example.com',
      user_name='홍길동',
      start_date=datetime(2026, 3, 1, 9, 0)
  )

╔══════════════════════════════════════════════════════════════════════╗
║  ⚠️  Gmail 사용 시 앱 비밀번호가 필요합니다.                        ║
║      python send_user_emails.py setup 명령으로 설정 가이드 확인    ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
