#!/usr/bin/env python3
"""간단 테스트 이메일"""
import sys
from real_email_sender import RealEmailSender
from datetime import datetime

# 수신 이메일 주소 (이전 로그에서 사용한 주소)
to_email = "ywamer2022@gmail.com"

print(f"📧 테스트 이메일 발송 중: {to_email}")
print()

sender = RealEmailSender()

result = sender.send_email(
    to_email=to_email,
    subject="[테스트] bty Training Team 이메일 시스템 확인 ✅",
    html_body=f"""
    <html>
    <body style="font-family: sans-serif; padding: 20px; line-height: 1.6;">
        <h2 style="color: #2C3E50;">✅ 이메일 발송 시스템 테스트 성공!</h2>
        
        <p>이 이메일을 받으셨다면 <strong>bty Training Team</strong> 이메일 발송 시스템이 정상 작동하고 있습니다! 🎉</p>
        
        <div style="background-color: #E8F8F5; padding: 20px; border-left: 4px solid #27AE60; margin: 20px 0; border-radius: 5px;">
            <h3 style="color: #27AE60; margin-top: 0;">📊 시스템 정보</h3>
            <p style="margin: 5px 0;">
                <strong>발송 시각:</strong> {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}<br/>
                <strong>프로그램:</strong> 28일 자기자비 여정<br/>
                <strong>팀:</strong> bty Training Team 💚<br/>
                <strong>상태:</strong> <span style="color: #27AE60; font-weight: bold;">정상 작동</span>
            </p>
        </div>
        
        <h3 style="color: #3498DB;">📋 최근 업데이트</h3>
        <ul style="line-height: 1.8;">
            <li>✅ 팀 이름을 "bty Training Team"으로 통일</li>
            <li>✅ "월요일" 표현 제거 (유연한 일정)</li>
            <li>✅ 응원 메시지 박스 추가</li>
            <li>✅ 발신자 이름 업데이트</li>
        </ul>
        
        <div style="background-color: #E8F8F5; padding: 15px; border-left: 4px solid #27AE60; margin: 20px 0;">
            <p style="margin: 0;"><strong>💚 응원 메시지</strong></p>
            <p style="margin: 5px 0 0 0;">완벽하지 않아도 괜찮습니다. 중요한 것은 방향입니다.<br/>
            매주 실천 가이드를 보내드리며, 당신의 여정을 함께하겠습니다.</p>
        </div>
        
        <p style="margin-top: 30px; border-top: 1px solid #E0E0E0; padding-top: 20px;">
            당신의 성장을 응원합니다.<br/>
            <strong>bty Training Team 💚</strong>
        </p>
    </body>
    </html>
    """
)

print()
if result['success']:
    print("=" * 70)
    print("🎉 테스트 성공!")
    print("=" * 70)
    print(f"✅ {to_email}로 이메일이 발송되었습니다.")
    print(f"📬 받은 편지함을 확인하세요.")
    print()
else:
    print("=" * 70)
    print("❌ 테스트 실패")
    print("=" * 70)
    print(f"오류: {result.get('error', '알 수 없는 오류')}")
    print()
