#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7개 이메일 발송 테스트
"""

from email_scheduler import EmailScheduler
from datetime import datetime
import os

# .env 파일 로드
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

print("="*70)
print("7개 이메일 스케줄 생성 및 발송 테스트")
print("="*70)
print()

# 샘플 데이터
user_email = "ywamer2022@gmail.com"
user_name = "테스트사용자"

analysis_results = {
    "scores": {"rosenberg": 22},
    "profile_type": "developing_critic",
    "detected_patterns": [
        {"type": "SELF_CRITICISM", "strength": 0.85},
        {"type": "PERFECTIONISM", "strength": 0.78}
    ],
    "hidden_strengths": [
        {"name": "회복탄력성", "description": "어려움 속에서도 다시 일어서는 힘"}
    ]
}

start_date = datetime.now()
retest_link = "https://example.com/retest"

# 스케줄러 생성
scheduler = EmailScheduler()

print("📅 이메일 스케줄 생성 중...")
schedule = scheduler.create_email_schedule(
    user_email=user_email,
    user_name=user_name,
    analysis_results=analysis_results,
    start_date=start_date,
    retest_link=retest_link,
    pdf_report_path=None
)

print(f"\n✅ 스케줄 생성 완료:")
print(f"   📧 수신자: {schedule['user_email']}")
print(f"   👤 이름: {schedule['user_name']}")
print(f"   📨 총 이메일 수: {schedule['total_emails']}")
print()

print("📋 이메일 발송 스케줄:")
for i, email in enumerate(schedule['emails'], 1):
    send_time = datetime.fromisoformat(email['send_at'])
    print(f"   {i}. [{email['type']}]")
    print(f"      발송 시각: {send_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"      제목: {email['subject'][:60]}...")
    if email.get('attachments'):
        print(f"      첨부 파일: {len(email['attachments'])}개")
    print()

print("="*70)
print(f"총 {schedule['total_emails']}개 이메일이 스케줄되었습니다.")
print("="*70)

# 실제 발송 테스트 (선택)
confirm = input("\n이 이메일들을 실제로 발송하시겠습니까? (y/n): ").strip().lower()
if confirm == 'y':
    print("\n📧 이메일 발송 중...")
    results = scheduler.send_all_emails_now(schedule)
    
    success_count = sum(1 for r in results if r.get('result', {}).get('success'))
    print(f"\n✅ {success_count}/{len(results)} 이메일 발송 성공!")
else:
    print("\n취소되었습니다.")
