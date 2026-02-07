#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 이메일 발송 시스템
SMTP를 사용한 실제 이메일 발송 구현
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional
from datetime import datetime
import json


class RealEmailSender:
    """실제 이메일 발송 클래스"""
    
    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = None,
        smtp_user: str = None,
        smtp_password: str = None,
        from_email: str = None,
        from_name: str = "자기자비 여정"
    ):
        """
        Args:
            smtp_host: SMTP 서버 주소 (예: smtp.gmail.com)
            smtp_port: SMTP 포트 (587 for TLS, 465 for SSL)
            smtp_user: SMTP 사용자명 (이메일)
            smtp_password: SMTP 비밀번호 또는 앱 비밀번호
            from_email: 발신자 이메일
            from_name: 발신자 이름
        """
        # 환경 변수에서 설정 가져오기
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = smtp_user or os.getenv('SMTP_USER')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        self.from_email = from_email or os.getenv('FROM_EMAIL', self.smtp_user)
        self.from_name = from_name or os.getenv('FROM_NAME', '자기자비 여정')
        
        # 로깅
        self.log_file = "email_send_log.txt"
        
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        attachments: List[Dict] = None,
        cc: List[str] = None,
        bcc: List[str] = None
    ) -> Dict:
        """
        실제 이메일 발송
        
        Args:
            to_email: 수신자 이메일
            subject: 제목
            html_body: HTML 본문
            attachments: 첨부 파일 리스트 [{"path": "...", "filename": "..."}]
            cc: 참조
            bcc: 숨은 참조
            
        Returns:
            발송 결과 딕셔너리
        """
        try:
            # SMTP 설정 확인
            if not self.smtp_user or not self.smtp_password:
                return {
                    "success": False,
                    "error": "SMTP 설정이 필요합니다. SMTP_USER와 SMTP_PASSWORD 환경 변수를 설정하세요.",
                    "to": to_email,
                    "subject": subject,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # HTML 본문 추가
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 첨부 파일 추가
            if attachments:
                for attachment in attachments:
                    if os.path.exists(attachment['path']):
                        with open(attachment['path'], 'rb') as f:
                            # PDF 파일은 명시적으로 application/pdf 타입 사용
                            filename = attachment['filename']
                            if filename.lower().endswith('.pdf'):
                                part = MIMEBase('application', 'pdf')
                            else:
                                part = MIMEBase('application', 'octet-stream')
                            
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            
                            # RFC 2231 인코딩을 사용한 한글 파일명 처리
                            from email.header import Header
                            
                            # 파일명을 UTF-8로 인코딩하고 RFC 2231 형식으로 설정
                            encoded_filename = filename.encode('utf-8')
                            part.add_header(
                                'Content-Disposition',
                                'attachment',
                                filename=('utf-8', '', filename)
                            )
                            
                            msg.attach(part)
            
            # SMTP 서버 연결 및 발송
            if self.smtp_port == 465:
                # SSL
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                # TLS
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            
            server.login(self.smtp_user, self.smtp_password)
            
            # 수신자 리스트
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            server.send_message(msg)
            server.quit()
            
            # 로그 기록
            log_entry = {
                "success": True,
                "to": to_email,
                "subject": subject,
                "attachments": len(attachments) if attachments else 0,
                "timestamp": datetime.now().isoformat()
            }
            self._log(log_entry)
            
            print(f"✅ 이메일 발송 성공: {to_email}")
            return log_entry
            
        except Exception as e:
            error_entry = {
                "success": False,
                "to": to_email,
                "subject": subject,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self._log(error_entry)
            
            print(f"❌ 이메일 발송 실패: {to_email}")
            print(f"   오류: {str(e)}")
            return error_entry
    
    def _log(self, entry: Dict):
        """로그 기록"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except:
            pass
    
    def send_batch_emails(
        self,
        emails: List[Dict]
    ) -> List[Dict]:
        """
        여러 이메일 일괄 발송
        
        Args:
            emails: 이메일 리스트 (각각 to, subject, body_html, attachments 포함)
            
        Returns:
            발송 결과 리스트
        """
        results = []
        
        for i, email_data in enumerate(emails, 1):
            print(f"\n[{i}/{len(emails)}] 발송 중...")
            
            result = self.send_email(
                to_email=email_data['to'],
                subject=email_data['subject'],
                html_body=email_data['body_html'],
                attachments=email_data.get('attachments', [])
            )
            
            results.append(result)
        
        # 요약 출력
        success_count = sum(1 for r in results if r['success'])
        print(f"\n{'='*70}")
        print(f"발송 완료: {success_count}/{len(emails)} 성공")
        print(f"{'='*70}")
        
        return results


def setup_gmail_smtp():
    """
    Gmail SMTP 설정 가이드
    
    Gmail을 사용하려면:
    1. Google 계정 > 보안 > 2단계 인증 활성화
    2. 앱 비밀번호 생성 (https://myaccount.google.com/apppasswords)
    3. 환경 변수 설정:
       export SMTP_HOST=smtp.gmail.com
       export SMTP_PORT=587
       export SMTP_USER=your-email@gmail.com
       export SMTP_PASSWORD=your-app-password
       export FROM_EMAIL=your-email@gmail.com
    """
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    Gmail SMTP 설정 가이드                            ║
╚══════════════════════════════════════════════════════════════════════╝

1. Google 계정 설정
   - https://myaccount.google.com/security 접속
   - "2단계 인증" 활성화 (필수)

2. 앱 비밀번호 생성
   - https://myaccount.google.com/apppasswords 접속
   - "앱 선택": 메일
   - "기기 선택": 기타 (사용자 지정 이름 입력)
   - 생성된 16자리 비밀번호 복사

3. 환경 변수 설정 (.env 파일 또는 시스템 환경 변수)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx (앱 비밀번호)
   FROM_EMAIL=your-email@gmail.com

4. Python 코드에서 사용
   from real_email_sender import RealEmailSender
   
   sender = RealEmailSender()
   sender.send_email(
       to_email='recipient@example.com',
       subject='테스트',
       html_body='<h1>안녕하세요</h1>'
   )

╔══════════════════════════════════════════════════════════════════════╗
║  ⚠️  중요: Gmail 앱 비밀번호는 일반 비밀번호가 아닙니다!          ║
║      2단계 인증을 활성화한 후 별도로 생성해야 합니다.              ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def test_email_sending():
    """이메일 발송 테스트"""
    
    print("="*70)
    print("이메일 발송 테스트")
    print("="*70)
    
    # 환경 변수 확인
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("\n❌ SMTP 설정이 없습니다.")
        print("\n다음 환경 변수를 설정하세요:")
        print("  SMTP_HOST=smtp.gmail.com")
        print("  SMTP_PORT=587")
        print("  SMTP_USER=your-email@gmail.com")
        print("  SMTP_PASSWORD=your-app-password")
        print("  FROM_EMAIL=your-email@gmail.com")
        print("\nGmail 사용 가이드:")
        setup_gmail_smtp()
        return False
    
    print(f"\n✅ SMTP 설정 확인:")
    print(f"   호스트: {os.getenv('SMTP_HOST', 'smtp.gmail.com')}")
    print(f"   포트: {os.getenv('SMTP_PORT', '587')}")
    print(f"   사용자: {smtp_user}")
    print(f"   발신자: {os.getenv('FROM_EMAIL', smtp_user)}")
    
    # 테스트 이메일 발송
    test_email = input("\n테스트 이메일을 받을 주소를 입력하세요: ").strip()
    
    if not test_email:
        print("이메일 주소가 입력되지 않았습니다.")
        return False
    
    print(f"\n📧 테스트 이메일 발송 중: {test_email}")
    
    sender = RealEmailSender()
    
    result = sender.send_email(
        to_email=test_email,
        subject="[테스트] 이메일 발송 시스템 확인",
        html_body="""
        <html>
        <body style="font-family: sans-serif; padding: 20px;">
            <h2 style="color: #2C3E50;">✅ 이메일 발송 시스템 테스트</h2>
            <p>이 이메일을 받으셨다면 이메일 발송 시스템이 정상 작동하고 있습니다!</p>
            
            <div style="background-color: #E8F8F5; padding: 15px; border-left: 4px solid #27AE60; margin: 20px 0;">
                <h3 style="color: #27AE60; margin-top: 0;">시스템 정보</h3>
                <p>
                    <strong>발송 시각:</strong> {timestamp}<br/>
                    <strong>시스템:</strong> 28일 매일 실천 가이드<br/>
                    <strong>상태:</strong> 정상 작동
                </p>
            </div>
            
            <p>다음 단계로 진단 완료 이메일을 발송할 수 있습니다.</p>
            
            <p style="margin-top: 30px;">
                감사합니다,<br/>
                자기자비 여정 팀 💚
            </p>
        </body>
        </html>
        """.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    
    if result['success']:
        print(f"\n🎉 테스트 성공! {test_email}로 이메일이 발송되었습니다.")
        print(f"   받은 편지함을 확인하세요.")
        return True
    else:
        print(f"\n❌ 테스트 실패: {result.get('error', '알 수 없는 오류')}")
        return False


# ==========================================
# 사용 예제
# ==========================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        # 설정 가이드 표시
        setup_gmail_smtp()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        # 테스트 발송
        test_email_sending()
    else:
        print("""
사용법:
  python real_email_sender.py setup   # Gmail 설정 가이드 보기
  python real_email_sender.py test    # 이메일 발송 테스트

또는 Python 코드에서:
  from real_email_sender import RealEmailSender
  
  sender = RealEmailSender()
  sender.send_email(
      to_email='user@example.com',
      subject='제목',
      html_body='<h1>내용</h1>'
  )
        """)
