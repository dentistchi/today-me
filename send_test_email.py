#!/usr/bin/env python3
"""
테스트 이메일 발송 스크립트
환경 변수를 통해 SMTP 설정을 입력받습니다.
"""
import os
import sys
from datetime import datetime

# real_email_sender import
from real_email_sender import RealEmailSender

def send_test_email():
    """테스트 이메일 발송"""
    print("=" * 70)
    print("테스트 이메일 발송 시스템")
    print("=" * 70)
    print()
    
    # 환경 변수 확인
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL', smtp_user)
    
    # SMTP 설정 확인
    if not smtp_user or not smtp_password:
        print("❌ SMTP 설정이 없습니다.")
        print()
        print("다음 환경 변수를 설정해주세요:")
        print("  export SMTP_USER=your-email@gmail.com")
        print("  export SMTP_PASSWORD=your-app-password")
        print("  export FROM_EMAIL=your-email@gmail.com (선택)")
        print()
        print("또는 .env 파일을 생성하세요:")
        print("  cp .env.example .env")
        print("  (그 다음 .env 파일을 편집하여 실제 값 입력)")
        return False
    
    print("✅ SMTP 설정 확인:")
    print(f"   SMTP_HOST: {os.getenv('SMTP_HOST', 'smtp.gmail.com')}")
    print(f"   SMTP_PORT: {os.getenv('SMTP_PORT', '587')}")
    print(f"   SMTP_USER: {smtp_user}")
    print(f"   FROM_EMAIL: {from_email}")
    print()
    
    # 수신자 이메일 입력
    to_email = input("📧 테스트 이메일을 받을 주소를 입력하세요: ").strip()
    
    if not to_email:
        print("❌ 이메일 주소가 입력되지 않았습니다.")
        return False
    
    print()
    print(f"📨 테스트 이메일 발송 중: {to_email}")
    print()
    
    # 이메일 발송
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
            
            <h3 style="color: #3498DB;">📋 다음 단계</h3>
            <ul style="line-height: 1.8;">
                <li>✅ 이메일 시스템 테스트 완료</li>
                <li>📊 진단 완료 이메일 발송 준비됨</li>
                <li>📅 주간 실천 가이드 이메일 준비됨</li>
                <li>📈 24시간 보고서 이메일 준비됨</li>
                <li>🎉 완주 축하 이메일 준비됨</li>
            </ul>
            
            <div style="background-color: #FEF5E7; padding: 15px; border-left: 4px solid #F39C12; margin: 20px 0; border-radius: 5px;">
                <p style="margin: 0;"><strong>💡 팁:</strong> 이제 실제 사용자에게 이메일을 보낼 준비가 되었습니다!</p>
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
        return True
    else:
        print("=" * 70)
        print("❌ 테스트 실패")
        print("=" * 70)
        print(f"오류: {result.get('error', '알 수 없는 오류')}")
        print()
        print("문제 해결 방법:")
        print("1. SMTP 설정이 올바른지 확인")
        print("2. Gmail인 경우 '앱 비밀번호' 사용 (일반 비밀번호 X)")
        print("3. 2단계 인증이 활성화되어 있는지 확인")
        print("4. 방화벽에서 SMTP 포트(587) 허용 확인")
        print()
        return False

if __name__ == "__main__":
    success = send_test_email()
    sys.exit(0 if success else 1)
