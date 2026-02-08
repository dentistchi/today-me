#!/usr/bin/env python3
"""모든 이메일 테스트 발송"""
from email_scheduler import EmailScheduler
from datetime import datetime, timedelta
import time

# SMTP 설정
import os
os.environ['SMTP_USER'] = 'ywamer2022@gmail.com'
os.environ['SMTP_PASSWORD'] = 'whfyckgxxsbugzbk'
os.environ['FROM_EMAIL'] = 'ywamer2022@gmail.com'
os.environ['FROM_NAME'] = 'bty Training Team'
os.environ['ENABLE_EMAIL'] = 'true'

print("=" * 70)
print("📧 전체 이메일 시스템 테스트")
print("=" * 70)
print()

# 테스트 사용자 정보
user_email = "ywamer2022@gmail.com"
user_name = "테스트사용자"

# 샘플 분석 결과
analysis_results = {
    "scores": {
        "rosenberg": 22,
        "dimensions": {
            "자기수용": 3.2,
            "자기가치": 2.8,
            "자기효능감": 3.5,
            "자기자비": 2.5,
            "사회적 연결": 3.0
        }
    },
    "profile_type": "developing_critic",
    "detected_patterns": [
        {
            "type": "SELF_CRITICISM",
            "strength": 0.85,
            "evidence": [2, 8, 14, 21, 28],
            "description": "실수나 실패 시 가혹한 자기비판",
            "research": "Gilbert, P. (2009). The Compassionate Mind."
        }
    ],
    "hidden_strengths": [
        {
            "name": "회복탄력성",
            "evidence": "50개의 질문에 끝까지 답했습니다.",
            "how_to_use": "힘든 순간에 '나는 이전에도 이겨냈다'고 상기하세요."
        }
    ]
}

# 시작 날짜 (오늘)
start_date = datetime.now()
retest_link = "https://example.com/retest"

# 이메일 스케줄러 생성
scheduler = EmailScheduler()

print(f"사용자: {user_name} ({user_email})")
print(f"시작 날짜: {start_date.strftime('%Y-%m-%d %H:%M')}")
print()

# 이메일 스케줄 생성
print("📋 이메일 스케줄 생성 중...")
schedule = scheduler.create_email_schedule(
    user_email=user_email,
    user_name=user_name,
    analysis_results=analysis_results,
    start_date=start_date,
    retest_link=retest_link,
    pdf_report_path=None  # PDF는 테스트에서 제외
)

print(f"✅ 총 {schedule['total_emails']}개 이메일 준비 완료")
print()

# 각 이메일 발송
print("=" * 70)
print("📨 이메일 발송 시작")
print("=" * 70)
print()

email_types = {
    "diagnosis_complete": "1️⃣  진단 완료 이메일",
    "week_1_start": "2️⃣  Week 1 시작 (자기자비 기초)",
    "week_2_start": "3️⃣  Week 2 시작 (완벽주의 내려놓기)",
    "week_3_start": "4️⃣  Week 3 시작 (공통 인간성 인식)",
    "week_4_start": "5️⃣  Week 4 시작 (안정적 자기가치)",
    "24h_report": "6️⃣  24시간 보고서",
    "completion_and_retest": "7️⃣  완주 축하 & 재검사"
}

success_count = 0
failed_count = 0

for i, email in enumerate(schedule['emails'], 1):
    email_type = email['type']
    display_name = email_types.get(email_type, f"이메일 {i}")
    
    print(f"{display_name}")
    print(f"   제목: {email['subject'][:60]}...")
    
    # 이메일 발송
    result = scheduler.send_email_now(email)
    
    if result.get('success'):
        print(f"   ✅ 발송 성공")
        success_count += 1
    else:
        print(f"   ❌ 발송 실패: {result.get('error', 'Unknown')}")
        failed_count += 1
    
    print()
    
    # 발송 간격 (Gmail 제한 방지)
    if i < len(schedule['emails']):
        time.sleep(1)

# 결과 요약
print("=" * 70)
print("📊 발송 완료")
print("=" * 70)
print(f"✅ 성공: {success_count}개")
print(f"❌ 실패: {failed_count}개")
print(f"📧 총 발송: {len(schedule['emails'])}개")
print()
print(f"📬 {user_email} 받은편지함을 확인하세요!")
print()
print("발송된 이메일 목록:")
for email_type, display_name in email_types.items():
    print(f"  {display_name}")
print()
print("=" * 70)
