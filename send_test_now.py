#!/usr/bin/env python3
"""테스트 이메일 즉시 발송"""
from real_email_sender import RealEmailSender
from datetime import datetime

# SMTP 설정
smtp_user = "ywamer2022@gmail.com"
smtp_password = "whfyckgxxsbugzbk"  # 공백 제거
to_email = "ywamer2022@gmail.com"

print("=" * 70)
print("📧 테스트 이메일 발송 중...")
print("=" * 70)
print()
print(f"발신: {smtp_user}")
print(f"수신: {to_email}")
print()

# 이메일 발송
sender = RealEmailSender(
    smtp_user=smtp_user,
    smtp_password=smtp_password,
    from_email=smtp_user,
    from_name="bty Training Team"
)

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
        
        <h3 style="color: #3498DB;">📋 최근 업데이트 사항</h3>
        <ul style="line-height: 1.8;">
            <li>✅ <strong>팀 이름 통일:</strong> "bty Training Team"으로 전면 변경</li>
            <li>✅ <strong>"월요일" 표현 제거:</strong> 유연한 프로그램 일정</li>
            <li>✅ <strong>응원 메시지 추가:</strong> 진단 완료 이메일에 응원 박스</li>
            <li>✅ <strong>발신자 이름 업데이트:</strong> 모든 이메일에서 일관된 브랜딩</li>
        </ul>
        
        <div style="background-color: #E8F8F5; padding: 15px; border-left: 4px solid #27AE60; margin: 20px 0;">
            <p style="margin: 0;"><strong>💚 응원 메시지</strong></p>
            <p style="margin: 5px 0 0 0;">완벽하지 않아도 괜찮습니다. 중요한 것은 방향입니다.<br/>
            매주 실천 가이드를 보내드리며, 당신의 여정을 함께하겠습니다.</p>
        </div>
        
        <h3 style="color: #3498DB;">📅 이메일 발송 준비 완료</h3>
        <ul style="line-height: 1.8;">
            <li>📊 진단 완료 이메일 (응원 메시지 포함)</li>
            <li>📅 주간 실천 가이드 (Week 1-4)</li>
            <li>📈 24시간 보고서 이메일</li>
            <li>🎉 28일 완주 축하 이메일</li>
        </ul>
        
        <div style="background-color: #FEF5E7; padding: 15px; border-left: 4px solid #F39C12; margin: 20px 0; border-radius: 5px;">
            <p style="margin: 0;"><strong>💡 다음 단계</strong></p>
            <p style="margin: 5px 0 0 0;">모든 시스템이 정상 작동하고 있습니다. 실제 사용자에게 이메일을 보낼 준비가 완료되었습니다!</p>
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
    print(f"📬 받은 편지함(또는 스팸 폴더)을 확인하세요.")
    print()
    print("발송된 내용:")
    print("  - 시스템 정상 작동 확인")
    print("  - 최근 업데이트 사항 (팀 이름, 월요일 제거, 응원 메시지)")
    print("  - bty Training Team 브랜딩")
    print()
else:
    print("=" * 70)
    print("❌ 테스트 실패")
    print("=" * 70)
    print(f"오류: {result.get('error', '알 수 없는 오류')}")
    print()
